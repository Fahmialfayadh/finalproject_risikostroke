from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StrokeInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    hypertension = db.Column(db.Integer)
    heart_disease = db.Column(db.Integer)
    glucose = db.Column(db.Float)
    bmi = db.Column(db.Float)
    smoking = db.Column(db.String(50))
    prediction = db.Column(db.Float)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    ever_married = db.Column(db.String(20))
    work_type = db.Column(db.String(50))
    residence = db.Column(db.String(50))
    bins = db.Column(db.Text)      # JSON
    contrib = db.Column(db.Text)   # JSON

    # nilai prediksi risiko

