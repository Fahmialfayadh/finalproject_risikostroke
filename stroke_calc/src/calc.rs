use std::collections::HashMap;
use crate::types::InputData;

pub const INTERCEPT: f64 = -0.18901998817349125;
pub const COEF_AGE: f64 = 0.932249;
pub const COEF_GLUCOSE: f64 = 0.359952;
pub const COEF_BMI: f64 = 0.678346;
pub const COEF_RESIDENCE: f64 = 0.447152;
pub const COEF_SMOKING: f64 = 0.287368;
pub const COEF_EVER_MARRIED: f64 = 0.008489;
pub const COEF_WORK_TYPE: f64 = -0.213577;
pub const COEF_GENDER: f64 = 1.356776;
pub const COEF_HYPERTENSION: f64 = 0.546766;
pub const COEF_HEART_DISEASE: f64 = 0.446268;

#[inline(always)]
pub fn get_age_bin(age: f64) -> (&'static str, f64) {
    if age < 40.0 {
        ("0-40", -2.608643)
    } else if age < 55.0 {
        ("40-55", -0.624399)
    } else if age < 70.0 {
        ("55-70", 0.569374)
    } else {
        ("70+", 1.452558)
    }
}

#[inline(always)]
pub fn get_glucose_bin(glucose: f64) -> (&'static str, f64) {
    if glucose < 100.0 {
        ("<100", -0.325935)
    } else if glucose < 140.0 {
        ("100-140", -0.256714)
    } else if glucose < 200.0 {
        ("140-200", 0.728938)
    } else {
        (">200", 1.061982)
    }
}

#[inline(always)]
pub fn get_bmi_bin(bmi: f64) -> (&'static str, f64) {
    if bmi < 18.5 {
        ("Underweight", -2.484215)
    } else if bmi < 25.0 {
        ("Normal", -0.519536)
    } else if bmi < 30.0 {
        ("Overweight", 0.403013)
    } else {
        ("Obese", 0.073295)
    }
}

pub fn calculate_score(
    data: &InputData,
) -> (
    f64,
    &'static str,
    f64,
    (&'static str, &'static str, &'static str),
    HashMap<&'static str, f64>,
) {
    let height_m = data.height / 100.0;
    let bmi = data.weight / (height_m * height_m);

    let (a_bin, woe_age) = get_age_bin(data.age);
    let (g_bin, woe_glucose) = get_glucose_bin(data.glucose);
    let (b_bin, woe_bmi) = get_bmi_bin(bmi);

    let woe_gender = match data.gender.as_str() {
        "Female" => -0.038153,
        "Male" => 0.047954,
        _ => 1.867237,
    };

    let woe_married = if data.ever_married == "Yes" {
        0.313736
    } else {
        -1.102875
    };

    let woe_work = match data.work_type.as_str() {
        "Private" => 0.040421,
        "Self-employed" => 0.518065,
        "Govt_job" => 0.036665,
        "children" => -2.651787,
        _ => -0.844592,
    };

    let woe_resid = if data.residence == "Urban" {
        0.068190
    } else {
        -0.075113
    };

    let woe_smk = match data.smoking.as_str() {
        "formerly smoked" => 0.515769,
        "smokes" => 0.096728,
        "Unknown" => -0.486865,
        _ => -0.027622,
    };

    let woe_hyper = if data.hypertension == 1 {
        1.0953638583036969
    } else {
        -0.21608308534363982
    };

    let woe_heart = if data.heart_disease == 1 {
        1.392570918553818
    } else {
        -0.1623678345990987
    };

    let mut contrib = HashMap::with_capacity(10);
    contrib.insert("age", COEF_AGE * woe_age);
    contrib.insert("glucose", COEF_GLUCOSE * woe_glucose);
    contrib.insert("bmi", COEF_BMI * woe_bmi);
    contrib.insert("residence", COEF_RESIDENCE * woe_resid);
    contrib.insert("smoking", COEF_SMOKING * woe_smk);
    contrib.insert("ever_married", COEF_EVER_MARRIED * woe_married);
    contrib.insert("work_type", COEF_WORK_TYPE * woe_work);
    contrib.insert("gender", COEF_GENDER * woe_gender);
    contrib.insert("hypertension", COEF_HYPERTENSION * woe_hyper);
    contrib.insert("heart_disease", COEF_HEART_DISEASE * woe_heart);

    let mut z = INTERCEPT;
    for val in contrib.values() {
        z += val;
    }

    let prob = 1.0 / (1.0 + (-z).exp());

    let level = if prob < 0.08 {
        "Low"
    } else if prob < 0.20 {
        "Moderate"
    } else {
        "High"
    };

    (prob, level, bmi, (a_bin, g_bin, b_bin), contrib)
}



//test performa
#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Instant;

    #[test]
    fn bench_100k_pure_rust() {
        let sample = InputData {
            age: 67.0,
            glucose: 228.69,
            height: 180.0,
            weight: 85.0,
            gender: "Male".to_string(),
            ever_married: "Yes".to_string(),
            work_type: "Private".to_string(),
            residence: "Urban".to_string(),
            smoking: "formerly smoked".to_string(),
            hypertension: 0,
            heart_disease: 1,
        };

        let start = Instant::now();
        for _ in 0..100_000 {
            // Hindari compiler dead-code elimination dengan black_box
            std::hint::black_box(calculate_score(&sample));
        }
        let elapsed = start.elapsed();

        //convert elapsed to seconds
        let elapsed_secs = elapsed.as_secs_f64();

        println!("\nWaktu 100.000 iterasi di Rust murni: {} detik", elapsed_secs);
    }
}