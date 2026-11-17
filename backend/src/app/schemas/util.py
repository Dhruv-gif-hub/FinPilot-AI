from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class Status(str, Enum):
    QUEUED = "queued"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentTaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentRunStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class OutBoxEventStatus(str, Enum):
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"

class Role(str, Enum):
    OWNER = "owner"
    ANALYST = "analyst"
    VIEWER = "viewer"

class TaskType(str, Enum):
    PAYMENT_INVESTIGATION = "payment_investigation"
    RECONCILIATION = "reconciliation"
    FINANCIAL_RESEARCH = "financial_research"

class EventType(str, Enum):
    AGENT_TASK_CREATED = "agent_task_created"
    AGENT_TASK_UPDATED = "agent_task_updated"
    AGENT_TASK_COMPLETED = "agent_task_completed"
    AGENT_TASK_FAILED = "agent_task_failed"

class ItemType(str, Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    ADJUSTMENT = "adjustment"


class CaseType(str, Enum):
      MISSING_SETTLEMENT = "missing_settlement"
      AMOUNT_MISMATCH = "amount_mismatch"
      DUPLICATE_SETTLEMENT_ITEM = "duplicate_settlement_item"
      UNMATCHED_SETTLEMENT_ITEM = "unmatched_settlement_item"
      CURRENCY_MISMATCH = "currency_mismatch"


@dataclass
class UserContext:
    user_id: UUID