import math
from flask import Flask, redirect, render_template, request, session
from models import db, StrokeInput
from flask import make_response



app = Flask(__name__)
# password admin
app.secret_key = "matdishebat"
ADMIN_PASSWORD = "fpmatdiskeren"
# ===========================
#  DATABASE CONFIG
# ===========================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stroke.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        pw = request.form.get("password", "")
        if pw == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return "Wrong admin password."

    return render_template("admin_login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin/login")

    # ambil data
    sort_key = request.args.get("sort", "prediction")
    order = request.args.get("order", "desc")
    reverse = (order == "desc")

    records = StrokeInput.query.all()
    sorted_records = merge_sort(records, sort_key, reverse)

    # render template
    response = make_response(render_template(
        "admin_panel.html",
        data=sorted_records,
        sort_key=sort_key,
        order=order
    ))

    # blok browser cache
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

# ===========================
#   VIEW DETAIL RECORD

@app.route("/admin/view/<int:id>")
def admin_view(id):
    if not session.get("admin"):
        return redirect("/admin/login")

    r = StrokeInput.query.get(id)

    # convert StrokeInput → format yang dipakai oleh result.html
    data_input = {
        "name": r.name,
        "age": r.age,
        "gender": r.gender,
        "glucose": r.glucose,
        "smoking": r.smoking,
        # field lain optional
    }

    # langsung hitung ulang dengan fungsi calc yg sudah ada
    prob, level, bmi, bins, contrib = calc({
        "name": r.name,
        "age": r.age,
        "weight": 70,   # placeholder jika data tidak ada
        "height": 170,
        "glucose": r.glucose,
        "gender": r.gender,
        "ever_married": "No",
        "work_type": "Private",
        "residence": "Urban",
        "smoking": r.smoking
    })

    response = make_response(render_template("result.html",
                                             prob=prob,
                                             level=level,
                                             bmi=bmi,
                                             bins=bins,
                                             contrib=contrib,
                                             data=data_input))

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

@app.route("/admin/delete/<int:id>")
def admin_delete(id):
    if not session.get("admin"):
        return redirect("/admin/login")

    record = StrokeInput.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()

    return redirect("/admin")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)   # hapus session admin
    return redirect("/")

# ===========================
#  MODEL PARAMS (LOGISTIC WOE)
# ===========================
coef = {
    "age": 0.977266,
    "glucose": 0.446222,
    "bmi": 0.677713,
    "residence": 0.420405,
    "smoking": 0.350521,
    "ever_married": -0.048892,
    "work_type": -0.184483,
    "gender": -1.221075,
}
intercept = -0.053809001723937384

# ===========================
#       WOE TABLES
# ===========================
woe_age = {"0-40": -2.608643, "40-55": -0.624399, "55-70": 0.569374, "70+": 1.452558}
woe_glucose = {"<100": -0.325935, "100-140": -0.256714, "140-200": 0.728938, ">200": 1.061982}
woe_bmi = {"Underweight": -2.484215, "Normal": -0.519536, "Overweight": 0.403013, "Obese": 0.073295}
woe_gender = {"Female": -0.038153, "Male": 0.047954, "Other": 1.867237}
woe_married = {"No": -1.102875, "Yes": 0.313736}
woe_work = {
    "Private": 0.040421, 
    "Self-employed": 0.518065, 
    "Govt_job": 0.036665,
    "children": -2.651787, 
    "Never_worked": -0.844592
}
woe_resid = {"Rural": -0.075113, "Urban": 0.068190}
woe_smk = {
    "never smoked": -0.027622, 
    "formerly smoked": 0.515769,
    "smokes": 0.096728, 
    "Unknown": -0.486865
}

# ===========================
#        BINNING
# ===========================
def age_bin(a):
    if a < 40: return "0-40"
    if a < 55: return "40-55"
    if a < 70: return "55-70"
    return "70+"

def glucose_bin(g):
    if g < 100: return "<100"
    if g < 140: return "100-140"
    if g < 200: return "140-200"
    return ">200"

def bmi_bin(b):
    if b < 18.5: return "Underweight"
    if b < 25: return "Normal"
    if b < 30: return "Overweight"
    return "Obese"

# ===========================
#    PREDICTION FUNCTION
# ===========================
def calc(data):
    bmi = data["weight"] / ((data["height"]/100)**2)
    a_bin = age_bin(data["age"])
    g_bin = glucose_bin(data["glucose"])
    b_bin = bmi_bin(bmi)

    woe_values = {
        "age": woe_age[a_bin],
        "glucose": woe_glucose[g_bin],
        "bmi": woe_bmi[b_bin],
        "gender": woe_gender[data["gender"]],
        "ever_married": woe_married[data["ever_married"]],
        "work_type": woe_work[data["work_type"]],
        "residence": woe_resid[data["residence"]],
        "smoking": woe_smk[data["smoking"]],
    }

    z = intercept
    contrib = {}

    for k in coef:
        c = coef[k] * woe_values[k]
        contrib[k] = c
        z += c

    prob = 1 / (1 + math.exp(-z))

    if prob < 0.08:
        level = "Low"
    elif prob < 0.20:
        level = "Moderate"
    else:
        level = "High"

    return prob, level, bmi, (a_bin, g_bin, b_bin), contrib


# ===========================
#     ROUTES
# ===========================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    form = request.form

    # Input aman
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
    }

    # Hitung prediksi WOE
    prob, level, bmi, bins, contrib = calc(data_input)

    # Simpan kalau user klik save
    if form.get("save") == "yes":
        record = StrokeInput(
            name=data_input["name"],
            age=data_input["age"],
            gender=data_input["gender"],
            hypertension=int(form.get("hypertension", 0)),
            heart_disease=int(form.get("heart_disease", 0)),
            glucose=data_input["glucose"],
            bmi=bmi,
            smoking=data_input["smoking"],
            prediction=float(prob)
        )
        db.session.add(record)
        db.session.commit()


    return render_template(
        "result.html",
        prob=prob,
        level=level,
        bmi=bmi,
        bins=bins,
        contrib=contrib,
        data=data_input
    )


# =================================
#         ALGORITMA REKURSIF
# =================================

# ============
#   SORTING (fungsinya ada di file utils.py)
# ============

from utils import merge_sort


# ===========================
#     RUN SERVER
# ===========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database siap → stroke.db dibuat")
    app.run(debug=True)





