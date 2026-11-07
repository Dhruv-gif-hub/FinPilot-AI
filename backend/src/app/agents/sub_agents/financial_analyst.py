from langchain.agents import create_agent

from ...schemas.agent import FinancialAnalysisResult
from ...tools.analytics.analyze_failure_breakdown import analyze_failure_breakdown
from ...tools.analytics.compare_payment_periods import compare_payment_periods
from ...tools.analytics.get_payment_metrics import get_payment_metrics
from ...tools.financial_operations.reconcilliation_discrepancies import (
    find_reconciliation_discrepancies,
)
from ..context import FinPilotContext
from ..llm import get_llm

financial_analyst = create_agent(
    model=get_llm(),
    tools=[
        analyze_failure_breakdown,
        get_payment_metrics,
        find_reconciliation_discrepancies,
        compare_payment_periods,
    ],

    context_schema=FinPilotContext,
    response_format=FinancialAnalysisResult,
    
    system_prompt="""
    You are FinPilot's financial analyst.

    Your task is to analyze authorized payment metrics.

    Rules:
    1. Use tools for actual financial data.
    2. Never invent counts, percentages, or dates.
    3. Distinguish percentage-point changes from relative
       percentage changes.
    4. Treat zero denominators as undefined rates.
    5. Do not infer causation from correlation.
    6. Do not create, update, or delete financial records.
    7. Return the observations, numerical evidence, and
       limitations needed by the outer workflow.
    """,
)