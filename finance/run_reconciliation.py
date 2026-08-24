from __future__ import annotations

import json
from pathlib import Path

try:
    from .generate_data import BANK_LEDGER_FILE, PAYMENTS_FILE, SETTLEMENTS_FILE, main as generate_data
    from .reconciler import reconcile_files
except ImportError:
    from generate_data import BANK_LEDGER_FILE, PAYMENTS_FILE, SETTLEMENTS_FILE, main as generate_data
    from reconciler import reconcile_files

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = PROJECT_ROOT / "data" / "finance" / "reconciliation_report.json"


def main() -> None:
    if not PAYMENTS_FILE.exists() or not SETTLEMENTS_FILE.exists() or not BANK_LEDGER_FILE.exists():
        generate_data()

    report = reconcile_files(PAYMENTS_FILE, SETTLEMENTS_FILE, BANK_LEDGER_FILE)
    REPORT_FILE.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")

    print("\n=== AI Finance Controller: Multi-Source Reconciliation ===")
    print(f"Records processed      : {report.total_records}")
    print(f"Fully reconciled       : {report.matched_records}")
    print(f"Exceptions             : {report.exception_records}")
    print(f"Match rate             : {report.match_rate:.2f}%")
    print(f"Expected amount        : ₹{report.total_expected_amount:,.2f}")
    print(f"Matched amount         : ₹{report.total_matched_amount:,.2f}")
    print(f"Exception amount       : ₹{report.exception_amount:,.2f}")
    print(f"Bank-source exceptions: {report.bank_exception_records}")
    print(f"\nReport saved to        : {REPORT_FILE}")

    print("\nTop exceptions:")
    for item in report.unresolved_results[:10]:
        print(f"- {item.payment_id}: {item.status} — {item.explanation}")


if __name__ == "__main__":
    main()
