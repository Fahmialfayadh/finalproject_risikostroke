use pyo3::prelude::*;

#[derive(FromPyObject, Clone, Debug)]
pub struct InputData {
    #[pyo3(item)]
    pub age: f64,
    #[pyo3(item)]
    pub glucose: f64,
    #[pyo3(item)]
    pub height: f64,
    #[pyo3(item)]
    pub weight: f64,
    #[pyo3(item)]
    pub gender: String,
    #[pyo3(item)]
    pub ever_married: String,
    #[pyo3(item)]
    pub work_type: String,
    #[pyo3(item)]
    pub residence: String,
    #[pyo3(item)]
    pub smoking: String,
    #[pyo3(item)]
    pub hypertension: i32,
    #[pyo3(item)]
    pub heart_disease: i32,
}