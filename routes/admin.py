import json
import os
from flask import Blueprint, make_response, redirect, render_template, request, session
from crypto.operations import decrypt_record
from crypto.operations.data_operations import decrypt_record
from models import db, StrokeRecord
from stroke_model import calculate_level
from utils import merge_sort, search
from crypto import encrypt_data, decrypt_data, decrypt_records
from stroke_model import calc


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin"):
        return redirect("/admin")

    return render_template("login.html")


@admin_bp.route("/", strict_slashes=False)
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin/login")

    # ambil parameter search
    q = request.args.get("q", "").strip()

    # ambil semua data
    _records = db.session.query(StrokeRecord).all()
    
    records = decrypt_records(_records)

    if q:
        records = search(records, q, ["name"])

    # SORT
    sort_key = request.args.get("sort", "risk_score")
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


from stroke_model import calc

@admin_bp.route("/view/<int:id>")
def admin_view(id):
    if not session.get("admin"):
        return redirect("/login")

    r = db.session.get(StrokeRecord, id)
    if not r:
        return "Record not found", 404

    # 1. Dekripsi data_input langsung dari payload
    data_input = decrypt_data(r.encrypted_payload)

    # 2. Hitung model untuk mendapatkan visual bins dan contrib
    prob, level, bmi, bins, contrib = calc(data_input)

    return render_template(
        "result.html",
        prob=r.risk_score,
        level=level,
        bmi=bmi,
        bins=bins,
        contrib=contrib,
        data=data_input,
    )

@admin_bp.route("/delete/<int:id>")
def admin_delete(id):
    if not session.get("admin"):
        return redirect("/admin/login")

    record = db.session.query(StrokeRecord).get(id)
    if record:
        db.session.delete(record)
        db.session.commit()

    return redirect("/admin")

