import math
from flask import Flask, render_template, request

app = Flask(__name__)

# ===========================
#  MODEL PARAMS
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
#        WOE TABLES
# ===========================
woe_age = {"0-40": -2.608643, "40-55": -0.624399, "55-70": 0.569374, "70+": 1.452558}
woe_glucose = {"<100": -0.325935, "100-140": -0.256714, "140-200": 0.728938, ">200": 1.061982}
woe_bmi = {"Underweight": -2.484215, "Normal": -0.519536, "Overweight": 0.403013, "Obese": 0.073295}
woe_gender = {"Female": -0.038153, "Male": 0.047954, "Other": 1.867237}
woe_married = {"No": -1.102875, "Yes": 0.313736}
woe_work = {"Private": 0.040421, "Self-employed": 0.518065, "Govt_job": 0.036665,
            "children": -2.651787, "Never_worked": -0.844592}
woe_resid = {"Rural": -0.075113, "Urban": 0.068190}
woe_smk = {"never smoked": -0.027622, "formerly smoked": 0.515769,
           "smokes": 0.096728, "Unknown": -0.486865}

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
#        RISK FUNCTION
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
        "residence": woe_resid[data["Residence_type"]],
        "smoking": woe_smk[data["smoking_status"]],
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
#          ROUTES
# ===========================
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
    form = request.form

    data_input = {
        "age": float(form["age"]),
        "weight": float(form["weight"]),
        "height": float(form["height"]),
        "glucose": float(form["glucose"]),
        "gender": form["gender"],
        "ever_married": form["ever_married"],
        "work_type": form["work_type"],
        "Residence_type": form["residence"],
        "smoking_status": form["smoking"],
    }

    prob, level, bmi, bins, contrib = calc(data_input)

    return render_template(
        "result.html",
        prob=prob,
        level=level,
        bmi=bmi,
        bins=bins,
        data=data_input,
        contrib=contrib
    )


if __name__ == "__main__":
    app.run(debug=True)
