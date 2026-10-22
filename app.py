import os
import dotenv
from flask import Flask, session
from assets.messages.messages import translations
from models import db
from routes import admin_bp, auth_bp, public_bp, user_bp

dotenv.load_dotenv()

app = Flask(__name__)
# Session Secret Key
app.secret_key = "matdishebat"

# ===========================
#  DATABASE CONFIG
# ===========================
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stroke.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# ===========================
#  CONTEXT PROCESSOR (I18N)
# ===========================
@app.context_processor
def inject_conf_var():
    lang = session.get("lang", "id")

    def t(key):
        return translations.get(lang, translations["id"]).get(key, key)

    return dict(t=t, lang=lang)


# ===========================
#  REGISTER BLUEPRINTS
# ===========================
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

# ===========================
#     RUN SERVER
# ===========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database siap → stroke.db dibuat")
    app.run(debug=True)
