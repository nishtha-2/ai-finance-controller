from __future__ import annotations

from pathlib import Path

from .finance_agent import FinanceAgent, load_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = PROJECT_ROOT / "data" / "finance" / "reconciliation_report.json"


def test_summary_uses_verified_metrics():
    agent = FinanceAgent(load_report(REPORT_FILE))
    result = agent.answer("What is our reconciliation match rate?", use_llm=False)
    assert result["intent"] == "summary"
    assert "72.50%" in result["answer"]
    assert result["tool_result"]["summary"]["records_processed"] == 120


def test_payment_lookup():
    agent = FinanceAgent(load_report(REPORT_FILE))
    result = agent.answer("Why did PAY-00017 not reconcile?", use_llm=False)
    assert result["intent"] == "payment_lookup"
    assert result["tool_result"]["payment"]["status"] == "missing_settlement"


def test_high_value_filter_is_deterministic():
    agent = FinanceAgent(load_report(REPORT_FILE))
    result = agent.answer("Show unresolved payments above ₹20000", use_llm=False)
    assert result["intent"] == "high_value_exceptions"
    assert all(row["expected_amount"] >= 20000 for row in result["tool_result"]["exceptions"])


def test_bank_exception_query():
    agent = FinanceAgent(load_report(REPORT_FILE))
    result = agent.answer("Which bank-ledger exceptions do we have?", use_llm=False)
    assert result["intent"] == "bank_exception_breakdown"
    assert sum(result["tool_result"]["breakdown"].values()) > 0


def test_largest_exception_query():
    agent = FinanceAgent(load_report(REPORT_FILE))
    result = agent.answer("Show the largest unresolved exceptions", use_llm=False)
    assert result["intent"] == "largest_exceptions"
    assert len(result["tool_result"]["exceptions"]) > 0
