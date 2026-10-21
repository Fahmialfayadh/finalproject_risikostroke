import json
import os
from flask import Blueprint, make_response, redirect, render_template, request, session
from models import db, StrokeInput
from stroke_model import calculate_level
from utils import merge_sort, search

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    admin_password = os.environ.get("ADMIN_PASSWORD", "")
    if request.method == "POST":
        pw = request.form.get("password", "")
        if pw and pw == admin_password:
            session["admin"] = True
            return redirect("/admin")
        return "Wrong admin password."

    return render_template("admin_login.html")


@admin_bp.route("/", strict_slashes=False)
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin/login")

    # ambil parameter search
    q = request.args.get("q", "").strip()

    # ambil semua data
    records = StrokeInput.query.all()

    # FILTER
    if q:
        records = search(records, q, ["name"])

    # SORT
    sort_key = request.args.get("sort", "prediction")
    order = request.args.get("order", "desc")
    reverse = order == "desc"

    sorted_records = merge_sort(records, sort_key, reverse)

    # kirim ke template
    response = make_response(
        render_template(
            "admin_panel.html",
            data=sorted_records,
            sort_key=sort_key,
            order=order,
        )
    )

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@admin_bp.route("/view/<int:id>")
def admin_view(id):
    if not session.get("admin"):
        return redirect("/admin/login")

    r = StrokeInput.query.get(id)
    if not r:
        return "Record not found", 404

    # Muat JSON bins & contrib dari database
    bins = json.loads(r.bins) if r.bins else ["-", "-", "-"]
    contrib = json.loads(r.contrib) if r.contrib else {}

    # Persiapkan data_input seperti form asli
    data_input = {
        "name": r.name,
        "age": r.age,
        "gender": r.gender,
        "glucose": r.glucose,
        "smoking": r.smoking,
        "weight": r.weight,
        "height": r.height,
        "ever_married": r.ever_married,
        "work_type": r.work_type,
        "residence": r.residence,
        "hypertension": r.hypertension,
        "heart_disease": r.heart_disease,
    }

    response = make_response(
        render_template(
            "result.html",
            prob=r.prediction,
            level=calculate_level(r.prediction),
            bmi=r.bmi,
            bins=bins,
            contrib=contrib,
            data=data_input,
        )
    )

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


@admin_bp.route("/delete/<int:id>")
def admin_delete(id):
    if not session.get("admin"):
        return redirect("/admin/login")

    record = StrokeInput.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()

    return redirect("/admin")


@admin_bp.route("/logout")
def admin_logout():
    session.pop("admin", None)  # hapus session admin
    return redirect("/")
