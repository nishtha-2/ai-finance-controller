from __future__ import annotations

from pathlib import Path

try:
    from .finance_agent import FinanceAgent, load_report
except ImportError:
    from finance_agent import FinanceAgent, load_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_FILE = PROJECT_ROOT / "data" / "finance" / "reconciliation_report.json"


def main() -> None:
    if not REPORT_FILE.exists():
        from .run_reconciliation import main as reconcile_main
        reconcile_main()

    agent = FinanceAgent(load_report(REPORT_FILE))
    print("\n=== AI Finance Controller Agent ===")
    print("Ask about reconciliation, exceptions, or a payment. Type 'exit' to stop.\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in {"exit", "quit"}:
            break
        if not query:
            continue

        result = agent.answer(query)
        print(f"\nAgent: {result['answer']}\n")
        if result.get("policy_context"):
            sources = ", ".join(item["source"] for item in result["policy_context"])
            print(f"Grounded in: {sources}\n")


if __name__ == "__main__":
    main()
