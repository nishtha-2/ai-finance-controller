# Settlement Reconciliation Policy

A captured payment should have exactly one settlement record. Missing settlements are unresolved exceptions and should be investigated before the merchant closes the batch.

A settlement amount is considered matched when it equals the captured payment amount within a ₹0.01 tolerance. Amount mismatches must remain visible as exceptions rather than being silently rounded or overridden.

A settlement date is considered operationally consistent when it falls within three calendar days of the payment date. A wider gap should be flagged for investigation because settlement timing may indicate a delayed or incorrect record.

Duplicate settlement records must not be netted away automatically. The finance controller should preserve every source record and surface the duplicate references to an operator.
