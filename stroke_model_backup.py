import math

# ===========================
#  MODEL PARAMS (LOGISTIC WOE)
# ===========================
coef = {
    "age": 0.932249,
    "glucose": 0.359952,
    "bmi": 0.678346,
    "residence": 0.447152,
    "smoking": 0.287368,
    "ever_married": 0.008489,
    "work_type": -0.213577,
    "gender": 1.356776,
    "hypertension": 0.546766,
    "heart_disease": 0.446268,
}
intercept = -0.18901998817349125

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
    "Never_worked": -0.844592,
}
woe_resid = {"Rural": -0.075113, "Urban": 0.068190}
woe_smk = {
    "never smoked": -0.027622,
    "formerly smoked": 0.515769,
    "smokes": 0.096728,
    "Unknown": -0.486865,
}

# ===========================
#        BINNING
# ===========================
def age_bin(a):
    if a < 40:
        return "0-40"
    if a < 55:
        return "40-55"
    if a < 70:
        return "55-70"
    return "70+"


def glucose_bin(g):
    if g < 100:
        return "<100"
    if g < 140:
        return "100-140"
    if g < 200:
        return "140-200"
    return ">200"


def bmi_bin(b):
    if b < 18.5:
        return "Underweight"
    if b < 25:
        return "Normal"
    if b < 30:
        return "Overweight"
    return "Obese"


def calculate_level(prob):
    if prob < 0.10:
        return "Low"
    elif prob < 0.4545:
        return "Moderate"
    else:
        return "High"


# ===========================
#    PREDICTION FUNCTION
# ===========================
def calc(data):
    bmi = data["weight"] / ((data["height"] / 100) ** 2)
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
        "hypertension": 1.0953638583036969 if data["hypertension"] == 1 else -0.21608308534363982,
        "heart_disease": 1.392570918553818 if data["heart_disease"] == 1 else -0.1623678345990987,
    }

    z = intercept  # bias awal
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

