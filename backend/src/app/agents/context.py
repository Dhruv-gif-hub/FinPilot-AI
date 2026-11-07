from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class FinPilotContext:
    user_id: UUID
    merchant_id: UUID

    previous_start: datetime
    previous_end: datetime

    current_start: datetime
    current_end: datetime
