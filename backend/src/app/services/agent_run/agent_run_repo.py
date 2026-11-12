from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.agent_runs import AgentRuns
from ...models.agent_tasks import AgentTask
from ...schemas.util import AgentRunStatus, AgentTaskStatus


class AgentRunRepository:

    @staticmethod
    async def start_run(
        session: AsyncSession,
        task_id: UUID,
    ) -> dict | None:

        now = datetime.now(timezone.utc)

        async with session.begin():

            stmt = (
                select(AgentTask)
                .where(AgentTask.id == task_id)
                .with_for_update()
            )

            result = await session.scalars(stmt)
            task = result.first()

            if task is None:
                raise LookupError("Agent task not found.")

            if task.status in {"completed", "cancelled"}:
                return None

            # Prevent concurrent workers from executing
            # the same active task.
            if (
                task.status == "running"
                and task.lease_expires_at is not None
                and task.lease_expires_at > now
            ):
                return None

            # Allocate attempt number while holding the task lock.
            attempt_stmt = select(
                func.coalesce(
                    func.max(AgentRuns.attempt_number),
                    0,
                ) + 1
            ).where(
                AgentRuns.task_id == task_id
            )

            attempt_result = await session.scalars(attempt_stmt)
            attempt_number = attempt_result.first()

            run = AgentRuns(
                task_id=task.id,
                attempt_number=attempt_number,
                status=AgentRunStatus.RUNNING,
                started_at=now,
            )

            session.add(run)

            task.status = AgentTaskStatus.RUNNING
            task.lease_expires_at = now + timedelta(minutes=10)

            await session.flush()

            # Return primitive data, not a detached ORM object.
            return {
                "task_id": task.id,
                "run_id": run.id,
                "attempt_number": attempt_number,
                "user_id": task.user_id,
                "merchant_id": task.merchant_id,
                "task_type": task.task_type,
                "prompt": task.instruction,
                "input_data": task.input_data,
            }

    @staticmethod
    async def complete_run(
        session: AsyncSession,
        *,
        task_id: UUID,
        run_id: UUID,
        result: dict,
    ) -> None:

        now = datetime.now(timezone.utc)

        async with session.begin():

            run = await session.get(
                AgentRuns,
                run_id,
                with_for_update=True,
            )

            task = await session.get(
                AgentTask,
                task_id,
                with_for_update=True,
            )

            if run is None or task is None:
                raise LookupError(
                    "Task or run not found."
                )

            run.status = AgentRunStatus.COMPLETED
            run.completed_at = now
            run.error_code = None
            run.error_message = None

            task.status = AgentTaskStatus.COMPLETED
            task.lease_expires_at = None
            task.result_summary = result


    @staticmethod
    async def fail_run(
        session: AsyncSession,
        *,
        task_id: UUID,
        run_id: UUID,
        error: str,
        retryable: bool,
    ) -> None:

        now = datetime.now(timezone.utc)

        async with session.begin():

            run = await session.get(
                AgentRuns,
                run_id,
                with_for_update=True,
            )

            task = await session.get(
                AgentTask,
                task_id,
                with_for_update=True,
            )

            if run is None or task is None:
                return

            run.status = AgentRunStatus.FAILED
            run.completed_at = now
            run.error_message = error[:4000]

            task.status = (
                AgentTaskStatus.QUEUED if retryable else AgentTaskStatus.FAILED
            )

            task.lease_expires_at = None