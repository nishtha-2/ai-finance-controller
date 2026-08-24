from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ReconciliationResult:
    payment_id: str
    expected_amount: float
    settled_amount: float | None
    status: str
    difference: float
    explanation: str
    settlement_ids: tuple[str, ...]
    bank_amount: float | None = None
    bank_difference: float | None = None
    bank_status: str | None = None
    bank_ledger_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReconciliationReport:
    total_records: int
    matched_records: int
    exception_records: int
    match_rate: float
    total_expected_amount: float
    total_matched_amount: float
    exception_amount: float
    fully_reconciled_records: int
    bank_exception_records: int
    results: list[ReconciliationResult]

    @property
    def unresolved_results(self) -> list[ReconciliationResult]:
        return [item for item in self.results if item.status != "matched"]

    @property
    def bank_unresolved_results(self) -> list[ReconciliationResult]:
        return [item for item in self.results if item.bank_status not in (None, "matched")]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["results"] = [asdict(item) for item in self.results]
        return payload


class ReconciliationEngine:
    """Deterministic three-source reconciliation engine.

    Source of truth:
      1. Payment records establish the expected amount.
      2. Settlement records establish the processor settlement.
      3. Bank ledger records establish the final posted cash movement.

    The LLM never calculates or decides financial truth.
    """

    def __init__(self, amount_tolerance: float = 0.01, date_tolerance_days: int = 3):
        self.amount_tolerance = amount_tolerance
        self.date_tolerance_days = date_tolerance_days

    @staticmethod
    def _money(value: str | float | int | None) -> float:
        return round(float(value or 0), 2)

    @staticmethod
    def _date(value: str) -> date:
        return date.fromisoformat(value)

    def reconcile(
        self,
        payments: Iterable[dict],
        settlements: Iterable[dict],
        bank_ledger: Iterable[dict] | None = None,
    ) -> ReconciliationReport:
        payment_rows = list(payments)
        bank_enabled = bank_ledger is not None
        settlement_groups: dict[str, list[dict]] = defaultdict(list)
        bank_groups: dict[str, list[dict]] = defaultdict(list)
        for settlement in settlements:
            settlement_groups[str(settlement["payment_id"])].append(settlement)
        for ledger in bank_ledger or []:
            bank_groups[str(ledger["payment_id"])].append(ledger)

        results: list[ReconciliationResult] = []
        total_expected = 0.0
        total_matched = 0.0

        for payment in payment_rows:
            payment_id = str(payment["payment_id"])
            expected = self._money(payment["amount"])
            total_expected += expected
            matches = settlement_groups.get(payment_id, [])
            bank_matches = bank_groups.get(payment_id, [])

            if not matches:
                results.append(ReconciliationResult(
                    payment_id, expected, None, "missing_settlement", expected,
                    "No settlement record was found for this captured payment.", (),
                    bank_amount=self._bank_total(bank_matches),
                    bank_difference=self._bank_difference(expected, bank_matches),
                    bank_status=(self._bank_state(bank_matches, expected) if bank_enabled else None),
                    bank_ledger_ids=tuple(str(row["ledger_id"]) for row in bank_matches),
                ))
                continue

            if len(matches) > 1:
                settled_total = round(sum(self._money(row["settled_amount"]) for row in matches), 2)
                results.append(ReconciliationResult(
                    payment_id, expected, settled_total, "duplicate_settlement",
                    round(settled_total - expected, 2),
                    f"Found {len(matches)} settlement records for one payment.",
                    tuple(str(row["settlement_id"]) for row in matches),
                    bank_amount=self._bank_total(bank_matches),
                    bank_difference=self._bank_difference(settled_total, bank_matches),
                    bank_status=self._bank_state(bank_matches),
                    bank_ledger_ids=tuple(str(row["ledger_id"]) for row in bank_matches),
                ))
                continue

            settlement = matches[0]
            settled = self._money(settlement["settled_amount"])
            difference = round(settled - expected, 2)
            amount_ok = abs(difference) <= self.amount_tolerance
            payment_date = self._date(str(payment["payment_date"]))
            settlement_date = self._date(str(settlement["settlement_date"]))
            day_gap = abs((settlement_date - payment_date).days)
            date_ok = day_gap <= self.date_tolerance_days

            if not amount_ok:
                status = "amount_mismatch"
                explanation = f"Expected ₹{expected:,.2f} but settlement reports ₹{settled:,.2f}."
            elif not date_ok:
                status = "date_mismatch"
                explanation = f"Settlement occurred {day_gap} days after payment; allowed window is {self.date_tolerance_days} days."
            else:
                status = "matched"
                explanation = "Payment amount and settlement date are within the configured matching rules."

            bank_amount = self._bank_total(bank_matches)
            bank_difference = self._bank_difference(settled, bank_matches)
            bank_status = self._bank_state(bank_matches, settled) if bank_enabled else None
            if status == "matched" and bank_status not in (None, "matched"):
                explanation += f" Settlement matched the payment, but bank ledger has a {bank_status} exception."
                status = f"bank_{bank_status}"

            if status == "matched":
                total_matched += expected

            results.append(ReconciliationResult(
                payment_id, expected, settled, status, difference, explanation,
                (str(settlement["settlement_id"]),),
                bank_amount=bank_amount,
                bank_difference=bank_difference,
                bank_status=bank_status,
                bank_ledger_ids=tuple(str(row["ledger_id"]) for row in bank_matches),
            ))

        total_records = len(results)
        matched_records = sum(item.status == "matched" for item in results)
        exception_records = total_records - matched_records
        match_rate = round((matched_records / total_records) * 100, 2) if total_records else 0.0
        exception_amount = round(total_expected - total_matched, 2)
        bank_exception_records = sum(item.bank_status not in (None, "matched") for item in results)

        return ReconciliationReport(
            total_records=total_records,
            matched_records=matched_records,
            exception_records=exception_records,
            match_rate=match_rate,
            total_expected_amount=round(total_expected, 2),
            total_matched_amount=round(total_matched, 2),
            exception_amount=exception_amount,
            fully_reconciled_records=matched_records,
            bank_exception_records=bank_exception_records,
            results=results,
        )

    def _bank_total(self, rows: list[dict]) -> float | None:
        if not rows:
            return None
        return round(sum(self._money(row["bank_amount"]) for row in rows), 2)

    def _bank_difference(self, expected: float, rows: list[dict]) -> float | None:
        total = self._bank_total(rows)
        return None if total is None else round(total - expected, 2)

    def _bank_state(self, rows: list[dict], expected_amount: float | None = None) -> str | None:
        if not rows:
            return "missing_ledger"
        if len(rows) > 1:
            return "duplicate_ledger"
        row = rows[0]
        if str(row.get("bank_status", "posted")).lower() == "reversed":
            return "reversed"
        if expected_amount is not None:
            bank_amount = self._money(row.get("bank_amount"))
            if abs(bank_amount - expected_amount) > self.amount_tolerance:
                return "amount_mismatch"
        return "matched"


def load_csv(path: str | Path) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def reconcile_files(
    payments_path: str | Path,
    settlements_path: str | Path,
    bank_ledger_path: str | Path | None = None,
) -> ReconciliationReport:
    engine = ReconciliationEngine()
    bank = load_csv(bank_ledger_path) if bank_ledger_path and Path(bank_ledger_path).exists() else []
    return engine.reconcile(load_csv(payments_path), load_csv(settlements_path), bank)
