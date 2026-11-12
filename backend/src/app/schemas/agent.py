from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class InvestigationPlan(BaseModel):
    needs_payment_metrics: bool = True
    needs_metrics_comparison: bool = True
    needs_document_search: bool = True
    needs_web_search: bool = False

    requires_analytics_agent: bool = True
    requires_research_agent: bool = True
    previous_start: datetime
    previous_end: datetime
    current_start: datetime
    current_end: datetime


class FinancialFinding(BaseModel):
    observation: str
    significance: str
    supporting_metric: str | None = None


class DiscrepancyInput(BaseModel):
    """
    Structured output produced by deterministic investigation tools.
    """

    transaction_id: UUID | None = None
    settlement_item_id: UUID | None = None

    case_type: Literal[
      "missing_settlement_item",
      "amount_mismatch",
      "multiple_settlement_items",
      "unlinked_settlement_item",
      "currency_mismatch",
    ]

    expected_amount: Decimal | None = None
    observed_amount: Decimal | None = None

    currency: str | None = None

    description: str

class ReconciliationResult(BaseModel):
    settlement_id: UUID

    discrepancies: list[DiscrepancyInput] = Field(
        default_factory=list
    )
    investigation_summary: str

class FinancialAnalysisResult(BaseModel):
    summary: str
    metrics: list[dict] = Field(default_factory=list)
    findings: list[FinancialFinding] = Field(
        default_factory=list
    )
    Reconciliation: ReconciliationResult | None = None
    limitations: list[str] = Field(
        default_factory=list
    )


class ResearchEvidence(BaseModel):
    document_id: list[str] = Field(
        default_factory=list
    )
    chunk_id: list[str] = Field(
        default_factory=list
    )
    source_type: Literal[
        "internal_document",
        "merchant_document",
        "financial_metric",
        "external_source",
    ]

    title: str
    claim: str
    excerpt: str | None = None


class ResearchResult(BaseModel):
    summary: str

    evidence: list[ResearchEvidence] = Field(
        default_factory=list
    )

    limitations: list[str] = Field(
        default_factory=list
    )


class ReportFinding(BaseModel):
    title: str
    description: str
    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ] = "low"

    evidence_ids: list[str] = Field(
        default_factory=list
    )


class ReportDraft(BaseModel):
    title: str
    executive_summary: str

    reporting_period: dict

    metrics: dict = Field(
        default_factory=dict
    )

    summary: str|None = None
    
    findings: list[ReportFinding] = Field(
        default_factory=list
    )

    evidence: list[ResearchEvidence] = Field(
        default_factory=list
    )

    recommended_actions: list[str] = Field(
        default_factory=list
    )

    limitations: list[str] = Field(
        default_factory=list
    )