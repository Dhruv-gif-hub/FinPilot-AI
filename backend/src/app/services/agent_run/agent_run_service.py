from uuid import UUID

from ...db.session import Session_local
from .agent_run_repo import AgentRunRepository


class AgentRunService:

    @staticmethod
    async def start(
        task_id: UUID
    ):
        async with Session_local() as session:
            return await AgentRunRepository.start_run(session=session, task_id=task_id)

    @staticmethod
    async def complete(
        *,
        task_id: UUID,
        run_id: UUID,
        result: dict
    ):
        async with Session_local() as session:
            return await AgentRunRepository.complete_run(session=session,task_id=task_id, 
                                                   run_id=run_id, result=result)

    @staticmethod
    async def fail(
        *,
        task_id: UUID,
        run_id: UUID,
        error: str,
        retryable: bool,
    ):
        async with Session_local() as session:
            return await AgentRunRepository.fail_run(session=session, task_id=task_id, 
                                    run_id=run_id, error=error, retryable=retryable)