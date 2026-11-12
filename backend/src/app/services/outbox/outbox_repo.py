from sqlalchemy.ext.asyncio import AsyncSession

from ...models.outbox_events import OutboxEvent


class OutboxRepository:

    @staticmethod
    async def create(
        session: AsyncSession,
        **kwargs,
    ) -> OutboxEvent:

        event = OutboxEvent(**kwargs)

        session.add(event)

        await session.flush()
        
        return event