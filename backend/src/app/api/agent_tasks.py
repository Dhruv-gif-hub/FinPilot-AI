from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import require_write_user
from ..db.db_instance import get_db
from ..schemas.agent_tasks import AgentTaskCreate, AgentTaskCreated
from ..services.agent_task.agent_task_service import AgentTaskService

router = APIRouter(prefix="/agent-tasks", tags=["Agent Tasks"])


@router.post("", response_model=AgentTaskCreated, status_code=status.HTTP_202_ACCEPTED)
async def submit_agent_task(
    db: Annotated[AsyncSession, Depends(get_db)],
    payload: AgentTaskCreate,

    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
    ), current_user = Depends(require_write_user)):

    try:

        result = await AgentTaskService.submit_task(
            session=db,
            user_id=current_user.id,
            request=payload,
            idempotency_key=idempotency_key,
        )

        return AgentTaskCreated(**result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
