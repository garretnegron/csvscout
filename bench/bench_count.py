"""Compare csvscout.count_rows against pure Python.

Usage:  python bench/bench_count.py
Creates bench/big.csv (~1M rows, ~40 MB) on first run.
Build in release mode first, or the Rust numbers will be misleadingly slow:
    maturin develop --release
"""
import csv
import random
import time
from pathlib import Path

import csvscout

BIG = Path(__file__).parent / "big.csv"
ROWS = 1_000_000


def make_file():
    print(f"Generating {BIG.name} ({ROWS:,} rows)...")
    rng = random.Random(42)
    with BIG.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "user", "amount", "country", "ts"])
        for i in range(ROWS):
            w.writerow([i, f"user_{rng.randint(1, 50_000)}",
                        round(rng.uniform(0, 500), 2),
                        rng.choice(["US", "DE", "BR", "IN", "JP", ""]),
                        f"2026-0{rng.randint(1, 9)}-1{rng.randint(0, 9)}"])


def python_count(path):
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        return sum(1 for _ in reader)


def timeit(label, fn):
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    print(f"{label:<22} {elapsed:8.3f}s   result={result:,}")
    return elapsed


if __name__ == "__main__":
    if not BIG.exists():
        make_file()
    py = timeit("python csv module", lambda: python_count(BIG))
    rs = timeit("csvscout (rust)", lambda: csvscout.count_rows(str(BIG)))
    print(f"\nRust is {py / rs:.1f}x faster")
