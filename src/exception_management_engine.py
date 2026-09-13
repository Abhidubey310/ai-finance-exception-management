"""Synthetic AI-assisted finance exception management engine."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

from ai_assistant import build_review_packet, create_assistant_summary, determine_review_control


REQUIRED_COLUMNS = {
    "exception_id",
    "process_area",
    "source_system",
    "entity",
    "counterparty",
    "expected_amount",
    "actual_amount",
    "currency",
    "exception_date",
    "days_open",
    "document_status",
    "approval_status",
    "reconciliation_status",
    "duplicate_indicator",
    "description",
}

OWNER_BY_PROCESS = {
    "O2C": "Revenue Operations",
    "P2P": "Accounts Payable",
    "R2R": "Financial Control",
    "Intercompany": "Intercompany Finance",
    "Treasury": "Treasury",
}


def validate_input(df: pd.DataFrame) -> None:
    """Validate the minimum structure required by the prototype."""
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if df.empty:
        raise ValueError("Input file contains no finance exceptions.")
    if df["exception_id"].isna().any():
        raise ValueError("Exception ID must not be blank.")
    unknown_processes = sorted(set(df["process_area"]) - set(OWNER_BY_PROCESS))
    if unknown_processes:
        raise ValueError(f"Unsupported process areas: {', '.join(unknown_processes)}")


def classify_exception(row: pd.Series) -> pd.Series:
    """Classify a finance exception using explainable deterministic rules."""
    description = str(row["description"]).lower()
    variance = abs(float(row["expected_amount"]) - float(row["actual_amount"]))

    if str(row["duplicate_indicator"]).upper() == "YES":
        exception_type = "Potential Duplicate"
        action = "Validate duplicate evidence and block or reverse only after approval"
    elif str(row["approval_status"]).upper() != "APPROVED":
        exception_type = "Approval Control"
        action = "Obtain required approval before transaction release or posting"
    elif str(row["document_status"]).upper() != "COMPLETE":
        exception_type = "Missing Documentation"
        action = "Obtain supporting evidence and reperform the control"
    elif str(row["reconciliation_status"]).upper() in {"UNMATCHED", "PARTIAL"}:
        exception_type = "Reconciliation Break"
        action = "Investigate source-to-ledger difference and document resolution"
    elif variance > 0.01:
        exception_type = "Amount Variance"
        action = "Validate amount variance against source documentation"
    elif any(term in description for term in ("mapping", "master", "data")):
        exception_type = "Data Quality"
        action = "Correct master/source data and rerun the affected process"
    else:
        exception_type = "Other Exception"
        action = "Route for finance review and confirm the appropriate control response"

    days_open = int(row["days_open"])
    expected_amount = float(row["expected_amount"])

    if variance >= 50000 or days_open >= 90 or (
        exception_type == "Approval Control" and expected_amount >= 100000
    ):
        severity = "Critical"
    elif variance >= 10000 or days_open >= 30 or (
        exception_type == "Potential Duplicate" and expected_amount >= 10000
    ):
        severity = "High"
    elif variance >= 1000 or days_open >= 10:
        severity = "Medium"
    else:
        severity = "Low"

    owner = OWNER_BY_PROCESS[row["process_area"]]
    reason = (
        f"{exception_type}; variance {row['currency']} {variance:,.2f}; "
        f"{days_open} days open; owner {owner}"
    )

    return pd.Series(
        {
            "exception_type": exception_type,
            "variance_amount": round(variance, 2),
            "severity": severity,
            "owner_team": owner,
            "recommended_action": action,
            "decision_reason": reason,
        }
    )


def create_management_summary(result: pd.DataFrame) -> pd.DataFrame:
    """Summarise exception count, exposure and variance by process and severity."""
    return (
        result.groupby(["process_area", "severity"], as_index=False)
        .agg(
            exception_count=("exception_id", "count"),
            expected_exposure=("expected_amount", "sum"),
            absolute_variance=("variance_amount", "sum"),
        )
        .sort_values(["process_area", "severity"])
    )


def run_engine(input_path: Path, actions_path: Path, summary_path: Path) -> pd.DataFrame:
    """Process synthetic finance exceptions and create controlled review outputs."""
    df = pd.read_csv(input_path)
    validate_input(df)

    df["exception_date"] = pd.to_datetime(df["exception_date"], errors="raise")
    df["expected_amount"] = pd.to_numeric(df["expected_amount"], errors="raise")
    df["actual_amount"] = pd.to_numeric(df["actual_amount"], errors="raise")
    df["days_open"] = pd.to_numeric(df["days_open"], errors="raise").astype(int)

    assessment = df.apply(classify_exception, axis=1)
    result = pd.concat([df, assessment], axis=1)

    controls = result.apply(determine_review_control, axis=1)
    result = pd.concat([result, controls], axis=1)
    result["review_packet"] = result.apply(build_review_packet, axis=1)
    result["assistant_summary"] = result.apply(create_assistant_summary, axis=1)

    severity_rank = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
    result["_severity_rank"] = result["severity"].map(severity_rank)
    result = result.sort_values(
        ["_severity_rank", "variance_amount", "days_open"],
        ascending=[True, False, False],
    ).drop(columns="_severity_rank")

    summary = create_management_summary(result)

    actions_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(actions_path, index=False)
    summary.to_csv(summary_path, index=False)
    return result


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        result = run_engine(
            root / "data" / "sample_finance_exceptions.csv",
            root / "outputs" / "example_exception_actions.csv",
            root / "outputs" / "example_management_summary.csv",
        )
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(
        f"Processed {len(result)} exceptions with expected exposure "
        f"{result['expected_amount'].sum():,.2f} and absolute variance "
        f"{result['variance_amount'].sum():,.2f}."
    )
    print(
        result[["exception_id", "process_area", "exception_type", "severity", "owner_team"]]
        .to_string(index=False)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
