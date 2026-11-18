import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select

from ..core.background_task.celery_setup import celery
from ..db.session import Session_local
from ..models.outbox_events import OutboxEvent
from ..schemas.util import OutBoxEventStatus

TASK_NAME = "app.workers.agent_tasks.execute_agent_task"


async def claim_outbox_events(
    batch_size: int = 20,
) -> list[dict]:

    now = datetime.now(timezone.utc)

    claimed = []

    async with Session_local.begin() as session:

        stmt = (
            select(OutboxEvent)
            .where(
                or_(
                    (
                        (OutboxEvent.status == "pending")
                        & (OutboxEvent.available_at <= now)
                    ),
                    (
                        (OutboxEvent.status == "publishing")
                        & (OutboxEvent.locked_until < now)
                    ),
                )
            )
            .order_by(OutboxEvent.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )

        result = await session.scalars(stmt)

        events = list(result.all())

        for event in events:

            event.status = OutBoxEventStatus.PUBLISHING
            event.attempt_count += 1
            event.locked_until = now + timedelta(minutes=2) 

            claimed.append(
                {
                    "id": str(event.id),
                    "event_type": event.event_type,
                    "payload": event.payload,
                    "attempts": event.attempt_count,
                }
            )

    return claimed


async def mark_published(event_id: str) -> None:

    from uuid import UUID

    async with Session_local.begin() as session:

        event = await session.get(
            OutboxEvent,
            UUID(event_id),
        )

        if event is None:
            return

        event.status = OutBoxEventStatus.PUBLISHED
        event.published_at = datetime.now(timezone.utc)
        event.locked_until = None
        event.last_error = None


async def mark_publish_failed(
    event_id: str,
    error: str,
    attempts: int,
) -> None:

    from uuid import UUID

    async with Session_local.begin() as session:

        event = await session.get(
            OutboxEvent,
            UUID(event_id),
        )

        if event is None:
            return

        # Exponential backoff, capped at 15 minutes.
        delay_seconds = min(
            2 ** min(attempts, 9),
            900,
        )

        event.status = (
            OutBoxEventStatus.FAILED if attempts >= 10 else OutBoxEventStatus.PENDING
        )

        event.available_at = (
            datetime.now(timezone.utc)
            + timedelta(seconds=delay_seconds)
        )

        event.locked_until = None
        event.last_error = error[:2000]


async def dispatch_pending_events() -> int:

    events = await claim_outbox_events()

    published_count = 0

    for event in events:

        try:

            task_id = event["payload"]["task_id"]

            # Celery's publisher is synchronous.
            # Run it outside the event loop.
            await asyncio.to_thread(
                celery.send_task,
                TASK_NAME,
                args=[task_id],
            )

            await mark_published(event["id"])

            published_count += 1

        except Exception as exc:

            await mark_publish_failed(
                event_id=event["id"],
                error=str(exc),
                attempts=event["attempts"],
            )

    return published_count

@celery.task(
    name="app.workers.outbox_dispatcher.dispatch_outbox"
)
def dispatch_outbox():

    return asyncio.run(
        dispatch_pending_events()
    )