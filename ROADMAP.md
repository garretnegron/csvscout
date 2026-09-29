# csvscout roadmap

Build a fast CSV profiler in Rust and use it from Python. Each milestone adds
one feature and teaches one group of Rust concepts. A milestone is done when
its tests pass.

**The loop you'll repeat for every change:**

```bash
maturin develop      # compile the Rust code and install it into your venv
pytest               # run the tests
```

---

## Milestone 0: Set up and build the example

**Goal:** get the provided `count_rows` function compiling and callable from Python.

1. Install Rust from https://rustup.rs (on Mac/Linux it's one `curl` command;
   on Windows run `rustup-init.exe`, which also offers to install the C++ build tools you need).
   Check it worked: `cargo --version`
2. In the `csvscout` folder, create a virtual environment and install the tools:
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install maturin pytest
   ```
3. Build and test:
   ```bash
   maturin develop
   pytest
   ```
   The first build downloads and compiles dependencies, so it takes a minute or two.
   Later builds are much faster.

**Done when:** the three Milestone 0 tests pass. The Milestone 1 tests *should*
fail with `PanicException: not yet implemented`. That failure is your next task.

**Try it:** `python -c "import csvscout; print(csvscout.count_rows('tests/data/sample.csv'))"`

**Bonus:** run `maturin develop --release` then `python bench/bench_count.py` to
see the speedup over Python's `csv` module. (Always benchmark with `--release`.
Debug builds skip optimizations and can be 10x slower.)

**Read before moving on:** every comment in `src/lib.rs`. Also skim chapters 1–3 of
[The Rust Book](https://doc.rust-lang.org/book/), a free online book.

---

## Milestone 1: `column_names(path) -> list[str]`

**Concepts:** `Result` and `?`, `String` vs `&str`, `Vec`, iterators, `.map()`, `.collect()`

**Hints:**
- Open the reader exactly like `count_rows` does.
- `reader.headers()` returns a `Result<&StringRecord, csv::Error>`. Use `.map_err(to_py_err)?`.
- A `StringRecord` can be iterated. Each item is a `&str` (a borrowed view of text).
- You need owned `String`s to return. `.to_string()` converts `&str` → `String`.
- Pattern: `thing.iter().map(|s| s.to_string()).collect()`
  (`|s| ...` is a closure, Rust's version of `lambda s: ...`)

**Done when:** `pytest` shows all Milestone 1 tests passing.

---

## Milestone 2: `null_counts(path) -> dict[str, int]`

Count empty cells per column. This is the first stat that's actually useful at work.

**Concepts:** `for` loops over records, indexing, `Vec<usize>`, `HashMap`, `.enumerate()`, `.zip()`

**Hints:**
- Read the headers first. Then make a counter vector: `let mut nulls = vec![0usize; headers.len()];`
- Loop over `reader.records()`. For each record, loop with `.iter().enumerate()` to get `(index, value)`.
- A value is null if `value.trim().is_empty()`. Later you can also treat `"NULL"`, `"NA"` as null.
- Return `HashMap<String, usize>` (add `use std::collections::HashMap;`). PyO3 converts it to a dict.
- Build it with `headers.iter().zip(nulls).map(|(h, n)| (h.to_string(), n)).collect()`.
- **Borrow-checker gotcha:** `reader.headers()` borrows the reader, and you can't keep that borrow
  while you also loop over records. Clone the headers first: `let headers = reader.headers().map_err(to_py_err)?.clone();`
  This error message will be your first real meeting with ownership. Read it carefully, because it explains itself.

**Remember:** register the new function in the `#[pymodule]` block, and remove the `skip` marker from the test.

---

## Milestone 3: Type inference

Add `infer_types(path) -> dict[str, str]` returning one of `"int"`, `"float"`, `"bool"`, `"string"` per column.

**Concepts:** `enum`, `match`, `str::parse::<i64>()`, `Option`, writing Rust unit tests

**Hints:**
- Define `enum ColType { Empty, Int, Float, Bool, Str }`. An enum is a type that can be exactly one of several variants.
- Write `fn classify(value: &str) -> ColType` that tries `value.parse::<i64>().is_ok()`, then `f64`, then `true`/`false`.
- Write `fn widen(current: ColType, seen: ColType) -> ColType` using `match`. Int + Float → Float, anything + Str → Str, and so on.
- Keep a `Vec<ColType>` and widen it as you scan rows.
- Add `#[derive(Clone, Copy, Debug, PartialEq)]` above the enum so you can copy and compare it.
- Test `classify` and `widen` in Rust directly with a `#[cfg(test)] mod tests { ... }` block and `cargo test`.

**Stretch:** detect `"date"` for `YYYY-MM-DD` values.

---

## Milestone 4: One call, full profile, a real Python class

Replace the separate functions with `profile(path) -> list[ColumnProfile]`, where
`ColumnProfile` has `.name`, `.dtype`, `.null_count`, `.min`, `.max`, `.mean` (numeric columns only).

**Concepts:** `struct`, `impl`, `Option<f64>`, `#[pyclass]`, `#[pyo3(get)]`, `__repr__`

**Hints:**
- `#[pyclass]` on a struct makes it a Python class. `#[pyo3(get)]` on a field makes it a read-only attribute.
- `Option<f64>` becomes `float | None` in Python, which is right for min/max on string columns.
- Keep running totals (`sum`, `count`, `min`, `max`) in a helper struct while scanning. Don't store all the values.
- Add a `#[pymethods] impl ColumnProfile { fn __repr__(&self) -> String { ... } }` so it prints nicely.
- This is now **one pass over the file** for all stats. That's where the speedup over pandas comes from.

---

## Milestone 5: Go fast

**Concepts:** release builds, the GIL, threads, the `rayon` crate

1. Extend the benchmark to compare `profile()` with `pandas.read_csv(...).describe()` and `.isna().sum()`.
2. Release the GIL while the Rust code runs so other Python threads keep working.
   Take `py: Python<'_>` as the first parameter and wrap the heavy work in
   `py.detach(|| { ... })` (older PyO3 versions and tutorials call this `allow_threads`).
3. Add `profile_many(paths: Vec<String>)` that profiles several files **in parallel** with
   `rayon` (`paths.par_iter().map(...)`). Real data lakes are many files, so this is a real-world win.

---

## Milestone 6: Distinct counts

Add `.distinct_count` to `ColumnProfile`.

1. First version: exact, with a `HashSet<String>` per column. Measure memory on a big file.
2. Second version: approximate with **HyperLogLog**. Implement it yourself (about 50 lines, a great
   exercise in hashing and bit operations), and compare accuracy against the exact version.

---

## Milestone 7: Ship it

- Add `csvscout.pyi` type stubs so editors autocomplete your functions.
- Add a GitHub Actions workflow using `PyO3/maturin-action` to build wheels for Linux, Mac and Windows.
- Publish to TestPyPI, then `pip install` it on another machine.
- Write a README with your benchmark numbers.

---

## When you get stuck

- Rust compiler errors are unusually helpful. Read the whole message, including the `help:` lines.
- `cargo clippy` suggests more idiomatic code.
- Docs: [PyO3 guide](https://pyo3.rs), [csv crate](https://docs.rs/csv), [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- Or paste the error and your code back to me, and I'll review it.
