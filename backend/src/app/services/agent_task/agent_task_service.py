from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.request_hash import generate_request_hash
from ...schemas.agent_tasks import AgentTaskCreate
from ...schemas.response import Report
from ...schemas.util import AgentTaskStatus, EventType
from ...services.report.ReportRepository import ReportRepository
from ..membership.user_merchant_service import MerchantMembershipService
from ..outbox.outbox_repo import OutboxRepository
from .agent_task_repo import AgentTaskRepository


class AgentTaskService:

    @staticmethod
    async def submit_task(
        session: AsyncSession,
        *,
        user_id: UUID,
        request: AgentTaskCreate,
        idempotency_key: str | None = None,
    ) -> dict:

        # 1. Validate the task type.
        allowed_types = {
            "payment_investigation",
            "financial_research",
            "reconciliation"
        }

        if request.task_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported task type.",
            )

        request_hash = generate_request_hash(
            user_id=user_id, 
            request=request
        )

        # 2. One database transaction for both records.
        async with session.begin():

            # 3. Verify the user's merchant membership.

            await MerchantMembershipService.verify_merchant_access(
                session=session,
                user_id=user_id,
                merchant_id=request.merchant_id,
            )
            response = None

            # 4. Handle a repeated client request.
            if idempotency_key:

                existing = (
                    await AgentTaskRepository
                    .get_by_idempotency_key(
                        session,
                        user_id=user_id,
                        merchant_id=request.merchant_id,
                        idempotency_key=idempotency_key,
                    )
                )

                if existing is not None and existing.request_hash == request_hash:
                    response = {
                        "task_id": existing.id,
                        "status": existing.status,
                        "message": "Existing task returned.",
                        "is_duplicate": True,
                    }

                else:

                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "Idempotency key has already been "
                            "used with a different request."
                        ),
                    )

            if response is None:
                # 5. Create AgentTask.
                task = await AgentTaskRepository.create(
                    session,
                    user_id=user_id,
                    merchant_id=request.merchant_id,
                    task_type=request.task_type,
                    instruction=request.prompt,
                    input_data=request.input_data,
                    request_hash=request_hash,
                    idempotency_key=idempotency_key,
                    status=AgentTaskStatus.QUEUED,
                )

                # 6. Create OutboxEvent.
                await OutboxRepository.create(
                    session,
                    event_type=EventType.AGENT_TASK_CREATED,
                    aggregate_id=task.id,
                    payload={
                        "task_id": str(task.id),
                    },
                    status="pending",
                    attempts=0,
                )

                # Both inserts commit together.

                response = {
                    "task_id": task.id,
                    "status": str(task.status),
                    "message": "Agent task accepted.",
                    "is_duplicate": False,
                }
            
            return response

    @staticmethod
    async def get_task_result(
        session: AsyncSession,
        *,
        task_id: UUID
    ):
        task = await AgentTaskRepository.get_by_task_id(
            session=session, task_id=task_id)
        if task is None:
            return None

        task_status = task.status

        if task.status != AgentTaskStatus.COMPLETED:
            messages = {
                "queued": "Task is waiting for execution.",
                "running": "Agent is processing your request.",
                "failed": "Task execution failed."
            }

            return Report(
                task_id=task.id,
                status=task_status,
                message=messages.get(
                    task_status.lower(),
                    "Task is being processed.",
                ),
                report=None,
            )

        # 3. Task is completed. Retrieve its report.
        report = await ReportRepository.get_by_task_id(
            session=session,
            task_id=task.id,
        )

        # 4. A completed task should have a persisted report.
        if report is None:
            raise RuntimeError(
                "Task is marked COMPLETED but its report is missing."
            )

        # 5. Return the report.
        return Report(
            task_id=task.id,
            status=task_status,
            message="Task completed successfully.",
            report={
                "report_id": report.id,
                "title": report.title,
                "summary": report.summary,
                "findings": report.evidence,
                "recommendations": report.recommendations,
            },
        )