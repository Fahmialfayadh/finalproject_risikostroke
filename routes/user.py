import os
from flask import Blueprint, make_response, redirect, render_template, request, session
from crypto import decrypt_data, decrypt_records
from models import db, StrokeRecord
from stroke_model import calc
from utils import merge_sort, search

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/", strict_slashes=False)
@user_bp.route("/history", methods=["GET"])
def user_history():
    if not session.get("user_id"):
        return redirect("/login")

    user_id = session["user_id"]

    # Ambil semua data milik user yang sedang login
    _records = db.session.query(StrokeRecord).filter_by(user_id=user_id).all()
    records = decrypt_records(_records)

    # Ambil parameter search
    q = request.args.get("q", "").strip()
    if q:
        records = search(records, q, ["name"])

    # Sorting
    sort_key = request.args.get("sort", "risk_score")
    order = request.args.get("order", "desc")
    reverse = order == "desc"

    sorted_records = merge_sort(records, sort_key, reverse)

    response = make_response(
        render_template(
            "user_history.html",
            data=sorted_records,
            sort_key=sort_key,
            order=order,
        )
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@user_bp.route("/view/<int:id>")
def user_view(id):
    if not session.get("user_id"):
        return redirect("/login")

    user_id = session["user_id"]

    # Pastikan HANYA bisa membuka rekam medis miliknya sendiri
    r = db.session.query(StrokeRecord).filter_by(id=id, user_id=user_id).first()
    if not r:
        return "Record not found", 404

    # Dekripsi payload data input
    data_input = decrypt_data(r.encrypted_payload)

    # Hitung model untuk menampilkan visualisasi level, bmi, bins, dan contrib
    prob, level, bmi, bins, contrib = calc(data_input)

    response = make_response(
        render_template(
            "result.html",
            prob=r.risk_score,
            level=level,
            bmi=bmi,
            bins=bins,
            contrib=contrib,
            data=data_input,
        )
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@user_bp.route("/delete/<int:id>")
def user_delete(id):
    if not session.get("user_id"):
        return redirect("/login")

    user_id = session["user_id"]

    # Pastikan HANYA bisa menghapus rekam medis miliknya sendiri
    record = db.session.query(StrokeRecord).filter_by(id=id, user_id=user_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()

    return redirect("/user/history")