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

The real question is therefore not only:

"Did this transaction reconcile?"

but also:

"Why did it fail, how much money is affected, and what should we investigate next?"

AI Finance Controller is designed to answer all three.
Solution

The system processes three independent financial sources.

1. Payment Records

Represents the expected financial transaction.

2. Processor Settlements

Represents how the payment was settled by the processor.

3. Bank Ledger

Represents the corresponding bank-side transaction.

These sources are reconciled through deterministic rules.

The resulting reconciliation report is then exposed to an AI Finance Agent.

The agent can answer natural-language questions about:

Reconciliation status
Exception counts
Financial impact
High-value exceptions
Bank discrepancies
Individual payment failures
Investigation steps
Why AI Is Used Carefully

Financial systems should not rely on an LLM to calculate financial truth.

Therefore, the architecture deliberately separates:

Deterministic Finance Logic

The reconciliation engine handles:

Record matching
Amount comparison
Date validation
Duplicate detection
Missing settlement detection
Bank reconciliation
Exception classification
Match-rate calculation
Financial totals
AI Reasoning

The AI Finance Agent handles:

Natural-language understanding
Finance tool selection
Explanation of reconciliation results
Exception investigation
Summary generation
Policy-grounded recommendations

The LLM does not decide whether two financial amounts match.

Instead:
Financial Records
       |
       v
Deterministic Engine
       |
       v
Verified Financial Result
       |
       v
AI Finance Agent
       |
       v
Human-readable Explanation
Financial Guardrails

The AI assistant can:

Explain an exception
Summarize reconciliation results
Identify important exceptions
Recommend investigation steps
Answer questions using verified finance tools

The AI assistant cannot:

Invent a settlement
Modify a financial amount
Override the reconciliation result
Mark an unresolved exception as resolved
Claim that a financial issue was fixed when the deterministic engine still reports it as unresolved

This creates a clear separation between:

Financial truth → deterministic code

and

Financial understanding → AI

Evaluation

The current synthetic evaluation batch contains:

Metric	Result
Records processed	120
Fully reconciled	87
Exceptions	33
Match rate	72.50%
Expected value	₹27,67,035.84
Reconciled value	₹19,35,169.04
Exception value	₹8,31,866.80
Bank-side exceptions	18
Exception Breakdown
Exception Type	Count
Bank amount mismatch	9
Missing settlement	7
Amount mismatch	6
Date mismatch	5
Duplicate settlement	4
Bank reversed	2

The evaluation dataset intentionally contains injected anomalies.

The objective is not to artificially maximize the reconciliation rate.

The objective is to demonstrate that the system can:

Reconcile clean transactions.
Detect problematic transactions.
Classify the reason for failure.
Quantify the financial impact.
Provide an investigation interface for finance teams.
Architecture
                         USER
                           |
                           v
                 +-------------------+
                 | FastAPI Backend   |
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 | Finance Agent     |
                 | Intent + Tools    |
                 +---------+---------+
                           |
              +------------+------------+
              |                         |
              v                         v
       +-------------+          +----------------+
       | Finance     |          | Policy         |
       | Tools       |          | Retrieval      |
       +------+------+          +--------+-------+
              |                          |
              +------------+-------------+
                           |
                           v
              +-------------------------+
              | Reconciliation Engine   |
              +------------+------------+
                           |
              +------------+------------+
              |            |            |
              v            v            v
          Payments    Settlements    Bank Ledger
                           |
                           v
                 Reconciliation Report
                           |
                           v
                     AI Explanation
                           |
                           v
                          USER
Reconciliation Flow
1. Load financial records
          ↓
2. Match payment ↔ settlement
          ↓
3. Validate amount
          ↓
4. Validate settlement date
          ↓
5. Detect duplicates
          ↓
6. Reconcile against bank ledger
          ↓
7. Classify exceptions
          ↓
8. Generate reconciliation report
          ↓
9. Expose results through finance tools
          ↓
10. AI explains and investigates results
AI Finance Agent

The AI agent uses deterministic finance tools rather than directly guessing from raw financial data.

Example questions:

What is our reconciliation rate?
How many exceptions do we have?
Why is our reconciliation rate only 72.5%?
What are the highest-value exceptions?
How many exceptions are related to the bank?
Why was PAY-00019 flagged?

The agent retrieves the appropriate finance information and produces a grounded explanation.

Dashboard

The project includes a web dashboard for viewing reconciliation results and interacting with the AI Finance Controller.

The dashboard provides:

Batch summary
Reconciliation rate
Reconciled records
Exception count
Financial impact
Exception breakdown
Individual exception details
AI-powered finance queries

The dashboard is served directly by the FastAPI application.

 Technology Stack
Backend
Python
FastAPI
Pydantic
Data Processing
Pandas
NumPy
AI
Qwen 2.5 3B
Ollama

The language model runs locally through Ollama.

Frontend
HTML
CSS
JavaScript
Testing
Pytest
Project Structure
AI_Finance_Controller/
│
├── data/
│   └── finance/
│       ├── payments.csv
│       ├── settlements.csv
│       ├── bank_ledger.csv
│       └── reconciliation_report.json
│
├── finance/
│   ├── __init__.py
│   ├── agent_tools.py
│   ├── api.py
│   ├── finance_agent.py
│   ├── generate_data.py
│   ├── policy_retriever.py
│   ├── reconciler.py
│   ├── run_agent.py
│   ├── run_reconciliation.py
│   ├── test_agent.py
│   ├── test_reconciler.py
│   │
│   └── dashboard/
│       └── index.html
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
Getting Started
Prerequisites

You need:

Python 3.11+
Ollama
Qwen 2.5 3B
1. Clone the Repository
git clone https://github.com/nishtha-2/ai-finance-controller.git
cd ai-finance-controller
2. Create a Virtual Environment
python3.11 -m venv .venv

Activate it on macOS/Linux:

source .venv/bin/activate

On Windows:

.venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
 Ollama Setup

Install Ollama:

https://ollama.com

Pull the model:

ollama pull qwen2.5:3b

Verify:

ollama list

You should see:

qwen2.5:3b

If Ollama is already running, you do not need to manually start another server.

 Generate the Finance Dataset

Run:

python -m finance.generate_data

This creates the synthetic payment, settlement, and bank ledger data used by the controller.

🔎 Run Reconciliation

Run:

python -m finance.run_reconciliation

This generates the reconciliation report used by the API and AI agent.

Run Tests

Run:

python -m pytest -q

The project contains automated tests for:

Reconciliation logic
Exception detection
Finance agent behavior
Start the Application

Run:

uvicorn finance.api:app --reload

The dashboard will be available at:

http://127.0.0.1:8000/

Swagger API documentation:

http://127.0.0.1:8000/docs
🔌 API Endpoints
Health
GET /api/health

Returns API health and report availability.

Summary
GET /api/summary

Returns:

Records processed
Reconciled records
Exception count
Match rate
Expected amount
Reconciled amount
Exception amount
Bank exceptions
Exceptions
GET /api/exceptions

Returns unresolved reconciliation exceptions.

High-value Exceptions
GET /api/exceptions/high-value

Allows finance teams to focus on high-impact discrepancies.

Exception Breakdown
GET /api/exceptions/breakdown

Returns exception counts by category.

Largest Exceptions
GET /api/exceptions/largest

Returns the largest unresolved exceptions.

Bank Exceptions
GET /api/exceptions/bank

Returns bank-related reconciliation exceptions.

Payment Lookup
GET /api/payment/{payment_id}

Retrieves reconciliation information for a specific payment.

AI Finance Query
GET /api/query?q=Why%20is%20our%20reconciliation%20rate%20only%2072.5%25?

Returns an AI-generated explanation grounded in the finance tools and reconciliation report.

Build Challenges & Technical Decisions
1. Preventing AI hallucinations in financial calculations

One of the biggest challenges was deciding how the LLM should interact with financial data.

A naive implementation could send raw transactions to an LLM and ask it to determine whether records match.

We avoided this because a language model can produce plausible but incorrect numerical reasoning.

Instead, we separated the system into:

Deterministic Reconciliation
            +
       AI Reasoning

The reconciliation engine performs the financial calculations, while the AI explains the verified results.

2. Reconciling Three Independent Sources

Another challenge was that reconciliation is not simply a payment-to-settlement comparison.

A payment can successfully match a processor settlement and still fail against the bank ledger.

We therefore introduced source-specific exception conditions covering:

Payment ↔ settlement mismatches
Missing settlements
Duplicate settlements
Settlement date differences
Settlement ↔ bank discrepancies
Bank reversals

This allows the system to preserve where the reconciliation actually failed.

3. Grounding AI Responses

The AI needed access to the actual financial state of the batch rather than relying on generic finance knowledge.

We solved this by giving the agent structured finance tools such as:

Summary
Exception retrieval
High-value exception analysis
Largest exception analysis
Bank exception analysis
Payment lookup

The agent uses these tools to obtain verified results before producing an explanation.

4. Testing Realistic Failures

Testing only successful transactions would not demonstrate the value of a reconciliation system.

We therefore created synthetic evaluation data containing deliberately injected anomalies such as:

Missing settlements
Amount mismatches
Date mismatches
Duplicate settlements
Bank amount mismatches
Bank reversals

This allowed the system to be evaluated on its ability to identify and classify exceptions.

 Design Principles
Deterministic Financial Truth

Financial calculations are performed by code, not generated by an LLM.

Grounded AI

The AI works with verified outputs from finance tools and policy context.

Explainability

Each exception retains the identifiers and financial information required for investigation.

Human-in-the-loop

The system can recommend investigation steps but does not automatically modify financial records.

Reproducibility

The repository contains the synthetic data and reconciliation logic required to reproduce the evaluation.

Current Results

The current evaluation demonstrates:

120 records processed
        ↓
87 fully reconciled
        ↓
33 exceptions detected
        ↓
72.50% reconciliation rate

The exception value is:

₹8,31,866.80

This allows the finance team to quantify not just how many transactions failed, but also the financial value requiring investigation.

 Limitations

This is a prototype built using synthetic financial data.

It does not connect to production Razorpay systems or real merchant/customer financial records.

The current implementation focuses on:

Reconciliation
Exception detection
Exception analysis
AI-assisted investigation

It does not automatically execute financial corrections or settlement operations.

🔮 Future Work

The architecture can be extended into a production finance-operations platform with:

Production Integrations
Payment gateway integrations
Bank APIs
Settlement APIs
Database-backed transaction processing
Intelligence
Historical anomaly detection
Transaction risk scoring
Pattern detection across settlement failures
Predictive exception identification
Operations
Exception assignment
Human approval workflows
Audit logs
Role-based access control
Finance-team feedback loops
Automated alerts
Automation
Automated investigation workflows
Suggested resolution actions
Exception prioritization
Continuous reconciliation
