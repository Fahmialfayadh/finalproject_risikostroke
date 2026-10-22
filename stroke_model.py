import stroke_calc
import time

try:
    import stroke_calc
    _calc = stroke_calc.calc
except ImportError:
    from stroke_model_backup import calc as _calc

# udah pake rust
def calc(data):
    prob, level, bmi, bins, contrib = _calc(data)
    return prob, level, bmi, bins, contrib

def calculate_level(prob):
    if prob < 0.10:
        return "Low"
    elif prob < 0.4545:
        return "Moderate"
    else:
        return "High"





if __name__ == "__main__":
    # Contoh penggunaan
    data_input = {
        "name": "John Doe",
        "age": 45,
        "weight": 80,
        "height": 175,
        "glucose": 120,
        "gender": "Male",
        "ever_married": "Yes",
        "work_type": "Private",
        "residence": "Urban",
        "smoking": "formerly smoked",
        "hypertension": 0,
        "heart_disease": 0,
    }
    total_time_rust = 0.0
    total_time_python = 0.0
    iterations = 100000
    for i in range(iterations):
        start_time = time.time()
        prob_rust, level_rust, bmi_rust, bins_rust, contrib_rust = calc(data_input)
        total_time_rust += time.time() - start_time

        start_time = time.time()
        prob_python, level_python, bmi_python, bins_python, contrib_python = old_calc(data_input)
        total_time_python += time.time() - start_time

    print(f"total time taken (Rust): {total_time_rust:.2f} seconds")
    print(f"total time taken (Python): {total_time_python:.2f} seconds")
