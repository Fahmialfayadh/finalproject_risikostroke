import json
from os import environ
from flask import Blueprint, make_response, redirect, render_template, request, session
from crypto.exceptions import CryptoMethodError
from models import db, StrokeInput
from pdf_generator import generate_pdf_report
from stroke_model import calc

from crypto import AES, DES, RC4, get_cipher, encrypt_data, decrypt_data

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    return render_template("about.html")


@public_bp.route("/calculator")
def calculator():
    return render_template("index.html")


@public_bp.route("/set_language/<language>")
def set_language(language):
    session["lang"] = language
    return redirect(request.referrer or "/")


@public_bp.route("/predict", methods=["POST"])
def predict():
    form = request.form

    # Ambil input dari user
    data_input = {
        "name": form.get("name", ""),
        "age": float(form.get("age", 0)),
        "weight": float(form.get("weight", 0)),
        "height": float(form.get("height", 1)),
        "glucose": float(form.get("glucose", 0)),
        "gender": form.get("gender", "Other"),
        "ever_married": form.get("ever_married", "No"),
        "work_type": form.get("work_type", "Private"),
        "residence": form.get("residence", "Urban"),
        "smoking": form.get("smoking", "Unknown"),
        "hypertension": int(form.get("hypertension", 0)),
        "heart_disease": int(form.get("heart_disease", 0)),
    }

    # Hitung model
    prob, level, bmi, bins, contrib = calc(data_input)

    entry = StrokeInput(
                name=data_input["name"],
                age=data_input["age"],
                gender=data_input["gender"],
                hypertension=data_input["hypertension"],
                heart_disease=data_input["heart_disease"],
                glucose=data_input["glucose"],
                bmi=bmi,
                smoking=data_input["smoking"],
                weight=data_input["weight"],
                height=data_input["height"],
                ever_married=data_input["ever_married"],
                work_type=data_input["work_type"],
                residence=data_input["residence"],
                prediction=prob,
                bins=json.dumps(bins),
                contrib=json.dumps(contrib),
            )

    encrypted_entry = encrypt_data(entry)  # Encrypt the entry data

    # Jika user memilih SAVE, baru simpan ke database
    if form.get("save") == "yes":

        db.session.add(encrypted_entry)
        db.session.commit()

    # Tampilkan hasil prediksi
    return render_template(
        "result.html",
        prob=prob,
        level=level,
        bmi=bmi,
        bins=bins,
        contrib=contrib,
        data=data_input,
    )


@public_bp.route("/download_pdf", methods=["POST"])
def download_pdf():
    # Recalculate using POST data to be safe and consistent
    form = request.form
    data_input = {
        "name": form.get("name", ""),
        "age": float(form.get("age", 0)),
        "weight": float(form.get("weight", 0)),
        "height": float(form.get("height", 1)),
        "glucose": float(form.get("glucose", 0)),
        "gender": form.get("gender", "Other"),
        "ever_married": form.get("ever_married", "No"),
        "work_type": form.get("work_type", "Private"),
        "residence": form.get("residence", "Urban"),
        "smoking": form.get("smoking", "Unknown"),
        "hypertension": int(form.get("hypertension", 0)),
        "heart_disease": int(form.get("heart_disease", 0)),
    }

    prob, level, bmi, bins, contrib = calc(data_input)

    # Bundle result data
    result = {
        "prob": prob,
        "level": level,
        "bmi": bmi,
        "bins": bins,
        "contrib": contrib,
    }

    # Generate PDF using new module
    pdf_buffer = generate_pdf_report(data_input, result)

    response = make_response(pdf_buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename=Stroke_Risk_Report_{data_input["name"]}.pdf'

    return response

