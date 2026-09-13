"""Provider-agnostic AI-assistant pattern for synthetic finance exceptions.

The public portfolio implementation is deliberately offline and deterministic.
It builds the same structured review packet that could be supplied to an
approved enterprise LLM, while making the control boundary easy to inspect.
"""

from __future__ import annotations

import json
import pandas as pd


def build_review_packet(row: pd.Series) -> str:
    """Return a structured evidence packet suitable for an AI review layer."""
    packet = {
        "exception_id": row["exception_id"],
        "process_area": row["process_area"],
        "exception_type": row["exception_type"],
        "severity": row["severity"],
        "owner_team": row["owner_team"],
        "expected_amount": round(float(row["expected_amount"]), 2),
        "actual_amount": round(float(row["actual_amount"]), 2),
        "variance_amount": round(float(row["variance_amount"]), 2),
        "currency": row["currency"],
        "days_open": int(row["days_open"]),
        "document_status": row["document_status"],
        "approval_status": row["approval_status"],
        "reconciliation_status": row["reconciliation_status"],
        "duplicate_indicator": row["duplicate_indicator"],
        "description": row["description"],
        "recommended_action": row["recommended_action"],
    }
    return json.dumps(packet, sort_keys=True)


def create_assistant_summary(row: pd.Series) -> str:
    """Create an explainable offline summary from deterministic evidence.

    A production implementation could replace this function with a governed LLM
    call that receives only the structured review packet and is prevented from
    taking transactional actions.
    """
    amount_text = f"{row['currency']} {float(row['variance_amount']):,.2f}"
    return (
        f"{row['severity']} {row['exception_type']} in {row['process_area']} for "
        f"{row['counterparty']}. Absolute variance is {amount_text} and the case "
        f"has been open {int(row['days_open'])} days. Route to {row['owner_team']}. "
        f"Suggested next step: {row['recommended_action']}."
    )


def determine_review_control(row: pd.Series) -> pd.Series:
    """Set human-review and escalation controls for the assistant output."""
    severity = str(row["severity"])
    approval_required = severity in {"Critical", "High"} or row["exception_type"] in {
        "Approval Control",
        "Potential Duplicate",
    }
    escalation_required = severity == "Critical" or int(row["days_open"]) >= 60

    return pd.Series(
        {
            "human_approval_required": "Yes" if approval_required else "Standard Review",
            "escalation_required": "Yes" if escalation_required else "No",
        }
    )
