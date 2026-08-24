# AI Finance Controller

### AI-powered multi-source payment reconciliation and exception intelligence

An AI Finance Controller that reconciles payment, processor settlement, and bank ledger records, identifies financial discrepancies, and uses grounded AI to explain exceptions and guide finance teams toward the next investigation step.

Built for the **Razorpay Buildathon — AI Finance Controller Track**.

---

## The Problem

Finance operations teams often reconcile payment records against processor settlements and bank statements manually.

As transaction volume grows, this creates several problems:

- Missing settlements can remain unnoticed.
- Payment and settlement amounts may differ.
- Duplicate settlements can cause incorrect financial reporting.
- Settlement dates may not align with payment records.
- Processor data may appear correct while the bank ledger contains discrepancies.
- Finance teams need to understand **why** an exception occurred, not just know that something failed.

The AI Finance Controller automates this reconciliation loop and surfaces the records that require human attention.

---

## What We Built

The system processes three independent financial sources:

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
       +-----------------------+
       |                       |
       v                       v
Fully Reconciled           Exceptions
                               |
                               v
                        AI Finance Agent
                               |
                               v
                     Grounded Explanation
