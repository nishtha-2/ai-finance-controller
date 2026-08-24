from .reconciler import ReconciliationEngine


def test_reconciles_exact_match_without_bank():
    payments = [{"payment_id": "P1", "amount": "100.00", "payment_date": "2026-08-01"}]
    settlements = [{"settlement_id": "S1", "payment_id": "P1", "settled_amount": "100.00", "settlement_date": "2026-08-02"}]
    report = ReconciliationEngine().reconcile(payments, settlements)
    assert report.matched_records == 1
    assert report.match_rate == 100.0


def test_reconciles_three_sources():
    payments = [{"payment_id": "P1", "amount": "100.00", "payment_date": "2026-08-01"}]
    settlements = [{"settlement_id": "S1", "payment_id": "P1", "settled_amount": "100.00", "settlement_date": "2026-08-02"}]
    bank = [{"ledger_id": "L1", "payment_id": "P1", "bank_amount": "100.00", "bank_date": "2026-08-03", "bank_status": "posted"}]
    report = ReconciliationEngine().reconcile(payments, settlements, bank)
    assert report.matched_records == 1
    assert report.results[0].bank_status == "matched"
    assert report.results[0].bank_difference == 0.0


def test_detects_missing_settlement():
    payments = [{"payment_id": "P1", "amount": "100.00", "payment_date": "2026-08-01"}]
    report = ReconciliationEngine().reconcile(payments, [])
    assert report.exception_records == 1
    assert report.results[0].status == "missing_settlement"


def test_detects_amount_mismatch():
    payments = [{"payment_id": "P1", "amount": "100.00", "payment_date": "2026-08-01"}]
    settlements = [{"settlement_id": "S1", "payment_id": "P1", "settled_amount": "90.00", "settlement_date": "2026-08-02"}]
    report = ReconciliationEngine().reconcile(payments, settlements)
    assert report.results[0].status == "amount_mismatch"
    assert report.results[0].difference == -10.0


def test_detects_duplicate_settlement():
    payments = [{"payment_id": "P1", "amount": "100.00", "payment_date": "2026-08-01"}]
    settlements = [
        {"settlement_id": "S1", "payment_id": "P1", "settled_amount": "100.00", "settlement_date": "2026-08-02"},
        {"settlement_id": "S2", "payment_id": "P1", "settled_amount": "100.00", "settlement_date": "2026-08-03"},
    ]
    report = ReconciliationEngine().reconcile(payments, settlements)
    assert report.results[0].status == "duplicate_settlement"


def test_detects_bank_amount_exception():
    payments = [{"payment_id": "P1", "amount": "100.00", "payment_date": "2026-08-01"}]
    settlements = [{"settlement_id": "S1", "payment_id": "P1", "settled_amount": "100.00", "settlement_date": "2026-08-02"}]
    bank = [{"ledger_id": "L1", "payment_id": "P1", "bank_amount": "95.00", "bank_date": "2026-08-03", "bank_status": "posted"}]
    report = ReconciliationEngine().reconcile(payments, settlements, bank)
    assert report.results[0].status == "bank_amount_mismatch"
    assert report.results[0].bank_difference == -5.0
    assert report.bank_exception_records == 1


def test_detects_bank_reversal():
    payments = [{"payment_id": "P1", "amount": "100.00", "payment_date": "2026-08-01"}]
    settlements = [{"settlement_id": "S1", "payment_id": "P1", "settled_amount": "100.00", "settlement_date": "2026-08-02"}]
    bank = [{"ledger_id": "L1", "payment_id": "P1", "bank_amount": "100.00", "bank_date": "2026-08-03", "bank_status": "reversed"}]
    report = ReconciliationEngine().reconcile(payments, settlements, bank)
    assert report.results[0].status == "bank_reversed"
    assert report.bank_exception_records == 1
