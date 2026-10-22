mod calc;
mod types;

use pyo3::prelude::*;
use std::collections::HashMap;
use types::InputData;

#[pyfunction(name = "calc")]
fn run_calc(
    data: InputData,
) -> (
    f64,
    &'static str,
    f64,
    (&'static str, &'static str, &'static str),
    HashMap<&'static str, f64>,
) {
    calc::calculate_score(&data)
}

#[pymodule]
fn stroke_calc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_calc, m)?)?;
    Ok(())
}