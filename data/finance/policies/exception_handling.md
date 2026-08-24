# Finance Exception Handling Policy

Every unresolved reconciliation exception should have a machine-readable reason, the affected payment identifier, expected amount, observed amount when available, and the source settlement identifiers.

High-value exceptions should be prioritised for manual review. For this demo, payments with an expected amount of ₹10,000 or more are considered high-value.

The AI assistant may explain an exception and recommend the next investigation step, but it must not invent a settlement, alter a financial amount, or claim that an exception was resolved when the deterministic reconciliation engine still marks it unresolved.
