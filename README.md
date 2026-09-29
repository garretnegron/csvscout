# csvscout

**Fast CSV profiling for Python, written in Rust.**

## Why I'm building this
The purpose of this project is to learn programming with Rust. I come from a Data Science background using SQL and Python for most projects.
Working through this build will improve my overall programming skills and improve my ability to solve complex problems.
As a data analyst who has worked on countless ETL pipeline builds, I wanted to create a library that would be (somewhat) useful for the work analysts and engineers do.

> [!NOTE]
> This project is `In Progress` and will be updated with no fixed schedule or timeline.

## What it does (so far)
```python
import csvscout
csvscout.count_rows("data.csv")      # -> 1000000
```

## Progress
- [x] Milestone 0: project setup, `count_rows`
- [x] Milestone 1: `column_names`
- [ ] Milestone 2: `null_counts`
- [ ] Milestone 3: type inference
- [ ] Milestone 4: full `profile()` with a Python class
- [ ] Milestone 5: speed (release the GIL, parallel files)
- [ ] Milestone 6: distinct counts (HyperLogLog)
- [ ] Milestone 7: publish to PyPI

See [ROADMAP.md](ROADMAP.md) for details.

## Building locally
```bash
python -m venv .venv && .venv\Scripts\activate
pip install maturin pytest
maturin develop
pytest
```

## Benchmarks
<!-- fill in after running bench/bench_count.py -->