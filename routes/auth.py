from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from db.base import db
from models.user import User
import os

auth_bp = Blueprint("auth", __name__)
admin_name = os.environ.get("ADMIN_USERNAME", None)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect("/calculator")

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username:
            error = "Username tidak boleh kosong."
        elif len(username) < 3 or len(username) > 50:
            error = "Username harus terdiri dari 3 hingga 50 karakter."
        elif not password:
            error = "Password tidak boleh kosong."
        elif len(password) < 6:
            error = "Password minimal terdiri dari 6 karakter."
        elif password != confirm_password:
            error = "Konfirmasi password tidak cocok."
        else:
            # Periksa apakah username sudah terdaftar
            existing_user = db.session.query(User).filter_by(username=username).first()
            if existing_user:
                error = "Username sudah digunakan. Silakan pilih username lain."
            else:
                # Hash password dengan Werkzeug
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()

                # Set session setelah registrasi berhasil
                session["user_id"] = new_user.id
                session["username"] = new_user.username
                return redirect("/calculator")

    return render_template("register.html", error=error)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect("/calculator")

    admin_name = "sangadmin"

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            error = "Username dan password wajib diisi."
        else:
            user = db.session.query(User).filter_by(username=username).first()
            if not user or not check_password_hash(user.password, password):
                error = "Username atau password salah."
            else:
                # Set session setelah login berhasil
                session["user_id"] = user.id
                session["username"] = user.username
                session["admin"] = False

                if user.username == "sangadmin":
                    session["admin"] = True
                return redirect("/calculator")

    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("admin", None)
    return redirect("/login")

