from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import require_read_user
from ..db.db_instance import get_db
from ..schemas.response import Report, ReportResponse
from ..services.agent_task.agent_task_service import AgentTaskService
from ..services.report.ReportService import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"],)

@router.get("/tasks/{task_id}", response_model=ReportResponse)
async def list_reports(
    merchant_id: UUID,
    task_id = Path(),
    current_user=Depends(require_read_user)):

    return await ReportService.list_reports(
        user_id=current_user.id,
        merchant_id=merchant_id,
        task_id=task_id
    )


@router.get("/{task_id}/result", response_model=Report)
async def get_report(
    session: Annotated[AsyncSession, Depends(get_db)],
    task_id = Path()):

    result = await AgentTaskService.get_task_result(
        session=session, task_id=task_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Agent task not found.",
        )

    return result