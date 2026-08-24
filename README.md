# AI Finance Controller

### AI-powered multi-source payment reconciliation and exception intelligence

An AI Finance Controller that reconciles payment, processor settlement, and bank ledger records, identifies financial discrepancies, and uses grounded AI to explain exceptions and guide finance teams toward the next investigation step.

Built for the Razorpay Buildathon — AI Finance Controller track.

---

## The Problem

Finance operations teams often reconcile payment records against processor settlements and bank statements manually.

This creates several problems:

- Large transaction batches are difficult to reconcile reliably.
- Missing settlements can remain unnoticed.
- Amount and date mismatches require manual investigation.
- Duplicate settlements can create incorrect financial reporting.
- Bank-side discrepancies may not be visible from processor data alone.
- Finance teams need explanations, not just a list of mismatches.

The AI Finance Controller automates this reconciliation loop and surfaces the records that require human attention.

---

## What It Does

The system processes three independent sources:

```text
Payment Records
      +
Processor Settlements
      +
Bank Ledger
      |
      v
Deterministic Reconciliation Engine
      |
      +----------------------+
      |                      |
      v                      v
Fully Reconciled          Exceptions
                              |
                              v
                       AI Finance Agent
                              |
                              v
                     Grounded Explanation