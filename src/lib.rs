// csvscout: fast CSV profiling, written in Rust, used from Python.
//
// Reading guide for Python developers:
//   use x::y;           ~ from x import y
//   fn f(a: &str) -> T  ~ def f(a: str) -> T   (types are required, not hints)
//   let x = 1;          ~ x = 1   (but immutable! use `let mut x` to allow changes)
//   PyResult<T>         ~ "returns T, or raises a Python exception"
//   ?                   ~ "if this failed, return the error right now" (like re-raising)
//   Ok(value)           ~ return value (the success case of a Result)

use pyo3::exceptions::PyIOError;
use pyo3::prelude::*;

/// Convert a CSV-crate error into a Python `OSError` so Python code can catch it.
///
/// Rust has no exceptions. Functions that can fail return a `Result`,
/// which is either `Ok(value)` or `Err(error)`. PyO3 turns an `Err(PyErr)`
/// into a real Python exception when it crosses back into Python.
fn to_py_err(e: csv::Error) -> PyErr {
    PyIOError::new_err(e.to_string())
}

/// Count the data rows in a CSV file (the header row is not counted).
///
/// This is the worked example. Read it line by line before starting Milestone 1.
#[pyfunction] // <- this attribute makes the function callable from Python
fn count_rows(path: &str) -> PyResult<usize> {
    // Open the file. `from_path` returns a Result, and `map_err` converts
    // the error type. `?` means "if it's an Err, return it from count_rows now".
    let mut reader = csv::Reader::from_path(path).map_err(to_py_err)?;

    // `usize` is an unsigned integer (can't be negative), the usual type for counts.
    let mut count: usize = 0;

    // `byte_records()` yields one Result per row. Using bytes instead of
    // strings skips UTF-8 validation, so it's faster when we only count.
    for record in reader.byte_records() {
        record.map_err(to_py_err)?; // raise if the row is malformed
        count += 1;
    }

    Ok(count)
}

/// Return the column names from the header row, e.g. ["id", "name", "age"].
///
/// MILESTONE 1: implement this. See ROADMAP.md for hints.
/// When you start, rename `_path` to `path` (the underscore just silences
/// the "unused variable" warning) and delete the `todo!()` line.
#[pyfunction]
fn column_names(_path: &str) -> PyResult<Vec<String>> {
    // Vec<String> is Rust's list of strings. PyO3 turns it into a Python list.
    todo!("Milestone 1: read the header row and return it as a Vec<String>")
}

/// The module definition: this is what `import csvscout` runs.
/// Every #[pyfunction] must be registered here or Python won't see it.
#[pymodule]
fn csvscout(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(count_rows, m)?)?;
    m.add_function(wrap_pyfunction!(column_names, m)?)?;
    Ok(())
}
