from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class FinPilotContext:
    user_id: UUID
    merchant_id: UUID