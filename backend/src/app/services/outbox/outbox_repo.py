from ...models.outbox_events import OutboxEvent
from sqlalchemy.ext.asyncio import AsyncSession

class OutboxRepository:

    @staticmethod
    async def create(
        session: AsyncSession,
        **kwargs,
    ) -> OutboxEvent:

        event = OutboxEvent(**kwargs)

        session.add(event)

        return event