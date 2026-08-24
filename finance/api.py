from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .agent_tools import (
    bank_exception_breakdown,
    exception_breakdown,
    find_payment,
    get_exceptions,
    high_value_exceptions,
    largest_exceptions,
    summarize,
)
from .finance_agent import FinanceAgent, load_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = PROJECT_ROOT / "data" / "finance" / "reconciliation_report.json"
DASHBOARD_DIR = PROJECT_ROOT / "finance" / "dashboard"

app = FastAPI(
    title="AI Finance Controller",
    version="1.0.0",
    description=(
        "Deterministic three-source payment reconciliation with a grounded AI finance agent. "
        "Financial truth is calculated by Python; the optional local LLM only explains verified results."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)


def get_agent() -> FinanceAgent:
    if not REPORT_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="Reconciliation report not found. Run: python -m finance.run_reconciliation",
        )
    return FinanceAgent(load_report(REPORT_FILE))


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard/")


if DASHBOARD_DIR.exists():
    app.mount("/dashboard", StaticFiles(directory=DASHBOARD_DIR, html=True), name="dashboard")


@app.get("/api/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "report_available": REPORT_FILE.exists(), "dashboard_available": DASHBOARD_DIR.exists()}


@app.get("/api/summary", tags=["reconciliation"])
def summary() -> dict:
    return summarize(get_agent().report)


@app.get("/api/exceptions", tags=["reconciliation"])
def exceptions(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    return {"exceptions": get_exceptions(get_agent().report, limit)}


@app.get("/api/exceptions/high-value", tags=["reconciliation"])
def high_value(
    minimum_amount: float = Query(default=10000, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    return {
        "minimum_amount_inr": minimum_amount,
        "exceptions": high_value_exceptions(get_agent().report, minimum_amount, limit),
    }


@app.get("/api/exceptions/breakdown", tags=["reconciliation"])
def breakdown() -> dict:
    return exception_breakdown(get_agent().report)


@app.get("/api/exceptions/largest", tags=["reconciliation"])
def largest(limit: int = Query(default=10, ge=1, le=100)) -> dict:
    return {"exceptions": largest_exceptions(get_agent().report, limit)}


@app.get("/api/exceptions/bank", tags=["reconciliation"])
def bank_exceptions() -> dict:
    return bank_exception_breakdown(get_agent().report)


@app.get("/api/payment/{payment_id}", tags=["reconciliation"])
def payment(payment_id: str) -> dict:
    result = find_payment(get_agent().report, payment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return result


@app.post("/api/query", tags=["ai-agent"])
def query(request: QueryRequest) -> dict:
    return get_agent().answer(request.query)


@app.get("/api/query", tags=["ai-agent"], include_in_schema=False)
def query_legacy(q: str = Query(min_length=1, max_length=500)) -> dict:
    """Backward-compatible GET endpoint; the dashboard uses POST."""
    return get_agent().answer(q)
