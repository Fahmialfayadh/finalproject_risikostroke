from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StrokeInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    hypertension = db.Column(db.Integer)
    heart_disease = db.Column(db.Integer)
    glucose = db.Column(db.Float)
    bmi = db.Column(db.Float)
    smoking = db.Column(db.String(50))
    prediction = db.Column(db.Float)  # nilai prediksi risiko

    def __init__(self, age, gender, hypertension, heart_disease, glucose, bmi, smoking, prediction):
        self.age = age
        self.gender = gender
        self.hypertension = hypertension
        self.heart_disease = heart_disease
        self.glucose = glucose
        self.bmi = bmi
        self.smoking = smoking
        self.prediction = prediction
