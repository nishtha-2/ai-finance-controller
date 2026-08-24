from __future__ import annotations

from dataclasses import asdict
from typing import Any

try:
    from .reconciler import ReconciliationReport
except ImportError:
    from reconciler import ReconciliationReport


def summarize(report: ReconciliationReport) -> dict[str, Any]:
    return {
        "records_processed": report.total_records,
        "fully_reconciled_records": report.fully_reconciled_records,
        "matched_records": report.matched_records,
        "exception_records": report.exception_records,
        "match_rate_percent": report.match_rate,
        "expected_amount_inr": report.total_expected_amount,
        "matched_amount_inr": report.total_matched_amount,
        "exception_amount_inr": report.exception_amount,
        "bank_exception_records": report.bank_exception_records,
    }


def get_exceptions(report: ReconciliationReport, limit: int = 20) -> list[dict[str, Any]]:
    exceptions = report.unresolved_results[: max(1, min(limit, 100))]
    return [asdict(item) for item in exceptions]


def find_payment(report: ReconciliationReport, payment_id: str) -> dict[str, Any] | None:
    payment_id = payment_id.strip().upper()
    for item in report.results:
        if item.payment_id.upper() == payment_id:
            return asdict(item)
    return None


def high_value_exceptions(report: ReconciliationReport, minimum_amount: float = 10000.0, limit: int = 20) -> list[dict[str, Any]]:
    rows = [item for item in report.unresolved_results if item.expected_amount >= minimum_amount]
    rows.sort(key=lambda item: item.expected_amount, reverse=True)
    return [asdict(item) for item in rows[: max(1, min(limit, 100))]]


def exception_breakdown(report: ReconciliationReport) -> dict[str, int]:
    breakdown: dict[str, int] = {}
    for item in report.unresolved_results:
        breakdown[item.status] = breakdown.get(item.status, 0) + 1
    return dict(sorted(breakdown.items(), key=lambda pair: (-pair[1], pair[0])))


def bank_exception_breakdown(report: ReconciliationReport) -> dict[str, int]:
    breakdown: dict[str, int] = {}
    for item in report.results:
        if item.bank_status and item.bank_status != "matched":
            breakdown[item.bank_status] = breakdown.get(item.bank_status, 0) + 1
    return dict(sorted(breakdown.items(), key=lambda pair: (-pair[1], pair[0])))


def largest_exceptions(report: ReconciliationReport, limit: int = 10) -> list[dict[str, Any]]:
    rows = sorted(report.unresolved_results, key=lambda item: item.expected_amount, reverse=True)
    return [asdict(item) for item in rows[: max(1, min(limit, 100))]]
