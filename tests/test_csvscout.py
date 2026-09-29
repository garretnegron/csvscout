from pathlib import Path

import pytest

import csvscout

DATA = Path(__file__).parent / "data"
SAMPLE = str(DATA / "sample.csv")
EMPTY = str(DATA / "empty.csv")


# ---------------------------------------------------------------- Milestone 0
def test_count_rows():
    assert csvscout.count_rows(SAMPLE) == 5


def test_count_rows_empty_file():
    assert csvscout.count_rows(EMPTY) == 0


def test_missing_file_raises_oserror():
    with pytest.raises(OSError):
        csvscout.count_rows(str(DATA / "does_not_exist.csv"))


# ---------------------------------------------------------------- Milestone 1
def test_column_names():
    assert csvscout.column_names(SAMPLE) == [
        "id", "name", "age", "score", "active", "signup_date",
    ]


def test_column_names_missing_file_raises_oserror():
    with pytest.raises(OSError):
        csvscout.column_names(str(DATA / "does_not_exist.csv"))


# ---------------------------------------------------------------- Milestone 2
# Remove the skip marker when you start Milestone 2.
@pytest.mark.skip(reason="Milestone 2")
def test_null_counts():
    assert csvscout.null_counts(SAMPLE) == {
        "id": 0, "name": 1, "age": 1, "score": 1, "active": 1, "signup_date": 1,
    }
