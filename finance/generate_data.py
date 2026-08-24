from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "finance"
PAYMENTS_FILE = OUTPUT_DIR / "payments.csv"
SETTLEMENTS_FILE = OUTPUT_DIR / "settlements.csv"
BANK_LEDGER_FILE = OUTPUT_DIR / "bank_ledger.csv"

PAYMENT_FIELDS = [
    "payment_id", "merchant_id", "customer_id", "order_id", "amount",
    "currency", "payment_status", "payment_date", "payment_method",
    "fee", "tax", "net_expected",
]

SETTLEMENT_FIELDS = [
    "settlement_id", "payment_id", "settled_amount", "settlement_date",
    "settlement_status", "reference",
]

BANK_LEDGER_FIELDS = [
    "ledger_id", "payment_id", "bank_amount", "bank_date",
    "bank_status", "bank_reference",
]


def generate_dataset(count: int = 120, seed: int = 42) -> tuple[list[dict], list[dict], list[dict]]:
    """Generate deterministic synthetic payment, settlement and bank-ledger data.

    The dataset deliberately contains multiple classes of exceptions across
    independent sources so the controller can demonstrate true multi-source
    reconciliation. No real customer or Razorpay data is used.
    """
    rng = random.Random(seed)
    start = date(2026, 8, 1)
    methods = ["card", "upi", "netbanking", "wallet"]
    payments: list[dict] = []
    settlements: list[dict] = []
    bank_ledger: list[dict] = []

    for i in range(1, count + 1):
        payment_id = f"PAY-{i:05d}"
        merchant_id = f"MER-{rng.randint(1, 4):03d}"
        customer_id = f"CUS-{rng.randint(1, 80):04d}"
        order_id = f"ORD-{i:06d}"
        amount = round(rng.uniform(250, 50000), 2)
        payment_date = start + timedelta(days=rng.randint(0, 20))
        fee = round(amount * 0.018, 2)
        tax = round(fee * 0.18, 2)
        net_expected = round(amount - fee - tax, 2)

        payments.append({
            "payment_id": payment_id,
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "order_id": order_id,
            "amount": f"{amount:.2f}",
            "currency": "INR",
            "payment_status": "captured",
            "payment_date": payment_date.isoformat(),
            "payment_method": rng.choice(methods),
            "fee": f"{fee:.2f}",
            "tax": f"{tax:.2f}",
            "net_expected": f"{net_expected:.2f}",
        })

        settlement_date = payment_date + timedelta(days=rng.randint(1, 3))
        settlement_amount = amount
        settlement_status = "settled"

        # Payment -> settlement exceptions.
        if i % 17 != 0:  # missing settlement
            if i % 19 == 0:
                settlement_amount = round(max(1, amount - rng.uniform(50, 500)), 2)
            elif i % 23 == 0:
                settlement_date = payment_date + timedelta(days=8)
            settlements.append({
                "settlement_id": f"SET-{i:05d}",
                "payment_id": payment_id,
                "settled_amount": f"{settlement_amount:.2f}",
                "settlement_date": settlement_date.isoformat(),
                "settlement_status": settlement_status,
                "reference": f"BANKREF-{i:07d}",
            })
            if i % 29 == 0:
                settlements.append({
                    "settlement_id": f"SET-DUP-{i:05d}",
                    "payment_id": payment_id,
                    "settled_amount": f"{amount:.2f}",
                    "settlement_date": (settlement_date + timedelta(days=1)).isoformat(),
                    "settlement_status": settlement_status,
                    "reference": f"BANKREF-DUP-{i:07d}",
                })

        # Settlement -> bank exceptions. Bank normally receives the settlement
        # amount, not necessarily the original payment amount.
        if i % 17 != 0:
            bank_amount = settlement_amount
            bank_date = settlement_date + timedelta(days=1)
            bank_status = "posted"
            if i % 13 == 0:
                bank_amount = round(max(1, settlement_amount - rng.uniform(20, 250)), 2)
            elif i % 37 == 0:
                bank_date = settlement_date + timedelta(days=9)
            elif i % 41 == 0:
                bank_status = "reversed"
            bank_ledger.append({
                "ledger_id": f"LED-{i:05d}",
                "payment_id": payment_id,
                "bank_amount": f"{bank_amount:.2f}",
                "bank_date": bank_date.isoformat(),
                "bank_status": bank_status,
                "bank_reference": f"BANK-{i:08d}",
            })

    return payments, settlements, bank_ledger


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    payments, settlements, bank_ledger = generate_dataset()
    write_csv(PAYMENTS_FILE, payments, PAYMENT_FIELDS)
    write_csv(SETTLEMENTS_FILE, settlements, SETTLEMENT_FIELDS)
    write_csv(BANK_LEDGER_FILE, bank_ledger, BANK_LEDGER_FIELDS)
    print(f"Generated {len(payments)} payments -> {PAYMENTS_FILE}")
    print(f"Generated {len(settlements)} settlements -> {SETTLEMENTS_FILE}")
    print(f"Generated {len(bank_ledger)} bank ledger rows -> {BANK_LEDGER_FILE}")


if __name__ == "__main__":
    main()
