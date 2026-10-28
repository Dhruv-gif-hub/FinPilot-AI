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

class Role(str, Enum):
    OWNER = "owner"
    ANALYST = "analyst"
    VIEWER = "viewer"

class TaskType(str, Enum):
    PAYMENT_INVESTIGATION = "payment_investigation"
    RECONCILIATION = "reconciliation"
    FINANCIAL_RESEARCH = "financial_research"

class ItemType(str, Enum):
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"
    ADJUSTMENT = "adjustment"


class CaseType(str, Enum):
      MISSING_SETTLEMENT = "missing_settlement"
      AMOUNT_MISMATCH = "amount_mismatch"
      DUPLICATE = "duplicate"
      UNMATCHED_TRANSACTION = "unmatched_transaction"
      UNMATCHED_SETTLEMENT_ITEM = "unmatched_settlement_item"
      CURRENCY_MISMATCH = "currency_mismatch"


@dataclass
class UserContext:
    user_id: UUID