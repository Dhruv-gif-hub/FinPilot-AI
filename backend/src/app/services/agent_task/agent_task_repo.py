from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.agent_tasks import AgentTask


class AgentTaskRepository:

    @staticmethod
    async def create(
        session: AsyncSession,
        **kwargs,
    ) -> AgentTask:

        task = AgentTask(**kwargs)

        session.add(task)

        return task

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        task_id: UUID,
    ) -> AgentTask | None:

        stmt = select(AgentTask).where(
            AgentTask.id == task_id
        )

        result = await session.scalars(stmt)

        return result.first()

    @staticmethod
    async def get_by_idempotency_key(
        session: AsyncSession,
        *,
        user_id: UUID,
        merchant_id: UUID,
        idempotency_key: str,
    ) -> AgentTask | None:

        stmt = select(AgentTask).where(
            AgentTask.user_id == user_id,
            AgentTask.merchant_id == merchant_id,
            AgentTask.idempotency_key == idempotency_key,
        )

        result = await session.scalars(stmt)

        return result.first()