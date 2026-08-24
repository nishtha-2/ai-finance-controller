from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

try:
    from ollama import chat
except ImportError:  # Optional dependency; deterministic mode still works.
    chat = None

try:
    from .agent_tools import bank_exception_breakdown, exception_breakdown, find_payment, get_exceptions, high_value_exceptions, largest_exceptions, summarize
    from .policy_retriever import retrieve_policy
    from .reconciler import ReconciliationReport
except ImportError:
    from agent_tools import bank_exception_breakdown, exception_breakdown, find_payment, get_exceptions, high_value_exceptions, largest_exceptions, summarize
    from policy_retriever import retrieve_policy
    from reconciler import ReconciliationReport


class FinanceAgent:
    """Tool-using finance assistant over deterministic reconciliation results.

    Financial values always come from Python tools. The optional LLM only turns
    those verified tool results into a natural-language explanation.
    """

    def __init__(self, report: ReconciliationReport, model: str = "qwen2.5:3b"):
        self.report = report
        self.model = model

    @staticmethod
    def _extract_payment_id(query: str) -> str | None:
        match = re.search(r"\bPAY-\d{5}\b", query.upper())
        return match.group(0) if match else None

    @staticmethod
    def _extract_amount(query: str, default: float = 10000.0) -> float:
        # Supports ₹10,000 / Rs 10000 / 10000 INR / 10000.
        match = re.search(r"(?:₹|RS\.?\s*|INR\s*)?([0-9][0-9,]*(?:\.\d+)?)\s*(?:INR|RUPEES)?", query, re.I)
        if not match:
            return default
        try:
            value = float(match.group(1).replace(",", ""))
            return value if value > 0 else default
        except ValueError:
            return default

    def _tool_call(self, query: str) -> dict[str, Any]:
        q = query.lower()
        payment_id = self._extract_payment_id(query)

        if payment_id:
            item = find_payment(self.report, payment_id)
            return {
                "intent": "payment_lookup",
                "payment": item,
                "found": item is not None,
            }

        if any(term in q for term in ("match rate", "reconciliation rate", "how many matched", "summary", "overview")):
            return {"intent": "summary", "summary": summarize(self.report)}

        if any(term in q for term in ("bank exception", "bank exceptions", "ledger exception", "ledger exceptions")):
            return {"intent": "bank_exception_breakdown", "breakdown": bank_exception_breakdown(self.report)}

        if any(term in q for term in ("breakdown", "types of exceptions", "exception types", "by reason")):
            return {"intent": "exception_breakdown", "breakdown": exception_breakdown(self.report)}

        if any(term in q for term in ("high value", "above", "over", "greater than")):

            threshold = self._extract_amount(query)
            rows = high_value_exceptions(self.report, minimum_amount=threshold)
            return {"intent": "high_value_exceptions", "minimum_amount_inr": threshold, "exceptions": rows}

        if any(term in q for term in ("largest", "biggest", "top exceptions")):
            return {"intent": "largest_exceptions", "exceptions": largest_exceptions(self.report, limit=10)}

        return {"intent": "exceptions", "exceptions": get_exceptions(self.report, limit=20)}

    @staticmethod
    def _format_currency(value: float | None) -> str:
        if value is None:
            return "N/A"
        return f"₹{value:,.2f}"

    def _deterministic_answer(self, tool_result: dict[str, Any]) -> str:
        intent = tool_result["intent"]

        if intent == "summary":
            s = tool_result["summary"]
            return (
                f"The batch contains {s['records_processed']} payments. "
                f"{s['matched_records']} matched and {s['exception_records']} remain unresolved, "
                f"giving a reconciliation match rate of {s['match_rate_percent']:.2f}%. "
                f"Expected value is {self._format_currency(s['expected_amount_inr'])}, "
                f"with {self._format_currency(s['exception_amount_inr'])} tied to exceptions."
            )

        if intent == "payment_lookup":
            item = tool_result["payment"]
            if not item:
                return "I could not find that payment in the reconciliation batch."
            settled = self._format_currency(item["settled_amount"])
            return (
                f"{item['payment_id']} is marked {item['status']}. "
                f"Expected {self._format_currency(item['expected_amount'])}; observed settlement {settled}. "
                f"{item['explanation']}"
            )

        if intent == "bank_exception_breakdown":
            breakdown = tool_result["breakdown"]
            if not breakdown:
                return "No bank-ledger exceptions were detected."
            parts = [f"{name}: {count}" for name, count in breakdown.items()]
            return "Bank-ledger exception breakdown — " + ", ".join(parts) + "."

        if intent == "exception_breakdown":
            breakdown = tool_result["breakdown"]
            if not breakdown:
                return "There are no unresolved exceptions in the batch."
            parts = [f"{name}: {count}" for name, count in breakdown.items()]
            return "Exception breakdown — " + ", ".join(parts) + "."

        rows = tool_result["exceptions"]
        if not rows:
            return "No matching unresolved exceptions were found."
        prefix = "High-value unresolved exceptions" if intent == "high_value_exceptions" else ("Largest unresolved exceptions" if intent == "largest_exceptions" else "Unresolved exceptions")
        lines = [prefix + ":"]
        for row in rows[:10]:
            lines.append(
                f"• {row['payment_id']} — {self._format_currency(row['expected_amount'])} — {row['status']}."
            )
        return "\n".join(lines)

    def answer(self, query: str, use_llm: bool = True) -> dict[str, Any]:
        tool_result = self._tool_call(query)
        policy_query = f"{query} {tool_result['intent']}"
        policies = retrieve_policy(policy_query, top_k=3)
        policy_context = [asdict(item) for item in policies]
        deterministic = self._deterministic_answer(tool_result)

        result = {
            "query": query,
            "intent": tool_result["intent"],
            "answer": deterministic,
            "tool_result": tool_result,
            "policy_context": policy_context,
            "grounded": True,
            "llm_used": False,
        }

        if use_llm and chat is not None:
            try:
                prompt = self._build_prompt(query, deterministic, tool_result, policy_context)
                response = chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = response["message"]["content"].strip()
                if text:
                    result["answer"] = text
                    result["llm_used"] = True
            except Exception as exc:
                result["llm_error"] = str(exc)

        return result

    @staticmethod
    def _build_prompt(query: str, verified_answer: str, tool_result: dict[str, Any], policies: list[dict[str, Any]]) -> str:
        return f"""You are an AI finance controller assistant operating over payment, processor-settlement, and bank-ledger sources.

Answer the user's question using ONLY the verified tool output and policy context below.
Do not invent amounts, transaction IDs, settlements, or resolutions. If the data says an
exception is unresolved, say it is unresolved. Keep the answer concise and businesslike.

USER QUESTION:
{query}

VERIFIED TOOL OUTPUT:
{json.dumps(tool_result, indent=2, default=str)}

DETERMINISTIC ANSWER:
{verified_answer}

POLICY CONTEXT:
{json.dumps(policies, indent=2, default=str)}

Return a clear answer with the relevant numbers and, when useful, the next investigation step.
"""


def load_report(path: str | Path) -> ReconciliationReport:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    results = []
    try:
        from .reconciler import ReconciliationResult
    except ImportError:
        from reconciler import ReconciliationResult

    for row in payload.get("results", []):
        row["settlement_ids"] = tuple(row.get("settlement_ids", []))
        results.append(ReconciliationResult(**row))

    return ReconciliationReport(
        total_records=payload["total_records"],
        matched_records=payload["matched_records"],
        exception_records=payload["exception_records"],
        match_rate=payload["match_rate"],
        total_expected_amount=payload["total_expected_amount"],
        total_matched_amount=payload["total_matched_amount"],
        exception_amount=payload["exception_amount"],
        fully_reconciled_records=payload.get("fully_reconciled_records", payload["matched_records"]),
        bank_exception_records=payload.get("bank_exception_records", 0),
        results=results,
    )
