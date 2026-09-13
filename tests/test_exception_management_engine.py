from pathlib import Path
import sys

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exception_management_engine import classify_exception, run_engine, validate_input  # noqa: E402


def load_sample() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "sample_finance_exceptions.csv")


def test_validate_input_rejects_missing_required_column():
    df = load_sample().drop(columns=["exception_id"])
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_input(df)


def test_approval_control_is_critical():
    row = load_sample().query("exception_id == 'EXC-005'").iloc[0]
    result = classify_exception(row)
    assert result["exception_type"] == "Approval Control"
    assert result["severity"] == "Critical"
    assert result["owner_team"] == "Treasury"


def test_duplicate_and_data_quality_routes_are_explainable():
    sample = load_sample()
    duplicate = classify_exception(sample.query("exception_id == 'EXC-006'").iloc[0])
    data_quality = classify_exception(sample.query("exception_id == 'EXC-009'").iloc[0])
    assert duplicate["exception_type"] == "Potential Duplicate"
    assert duplicate["severity"] == "High"
    assert data_quality["exception_type"] == "Data Quality"
    assert data_quality["severity"] == "Low"


def test_end_to_end_outputs(tmp_path):
    result = run_engine(
        ROOT / "data" / "sample_finance_exceptions.csv",
        tmp_path / "actions.csv",
        tmp_path / "summary.csv",
    )

    assert len(result) == 14
    assert result["variance_amount"].sum() == pytest.approx(143200.0)
    assert result["severity"].value_counts().to_dict() == {
        "Medium": 6,
        "High": 4,
        "Critical": 2,
        "Low": 2,
    }
    assert result.query("exception_id == 'EXC-003'")["escalation_required"].iloc[0] == "Yes"
    assert "EXC-003" in result.query("exception_id == 'EXC-003'")["review_packet"].iloc[0]
    assert (tmp_path / "actions.csv").exists()
    assert (tmp_path / "summary.csv").exists()
