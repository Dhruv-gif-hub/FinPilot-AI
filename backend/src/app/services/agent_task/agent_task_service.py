from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.agent_tasks import AgentTaskCreate
from ...schemas.util import AgentTaskStatus, OutBoxEventStatus
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
            raise ValueError("Unsupported task type.")

        # 2. One database transaction for both records.
        async with session.begin():

            # 3. Verify the user's merchant membership.
            #
            # Implement this using your actual UserMerchant model.
            # Do not omit it in the real application.
            if MerchantMembershipService is None:
                raise RuntimeError(
                    "Merchant membership validation is not configured."
                )

            await MerchantMembershipService.verify_merchant_access(
                session=session,
                user_id=user_id,
                merchant_id=request.merchant_id,
            )

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

                if existing is not None:
                    return {
                        "task_id": existing.id,
                        "status": str(existing.status),
                        "message": "Existing task returned.",
                    }

            # 5. Create AgentTask.
            task = await AgentTaskRepository.create(
                session,
                user_id=user_id,
                merchant_id=request.merchant_id,
                task_type=request.task_type,
                instruction=request.prompt,
                input_data=request.input_data,
                idempotency_key=idempotency_key,
                status=AgentTaskStatus.QUEUED,
            )

            # 6. Create OutboxEvent.
            await OutboxRepository.create(
                session,
                event_type=OutBoxEventStatus.PENDING,
                aggregate_id=task.id,
                payload={
                    "task_id": str(task.id),
                },
                status="pending",
                attempts=0,
            )

            # Both inserts commit together.

            return {
                "task_id": task.id,
                "status": str(task.status),
                "message": "Agent task accepted.",
            }