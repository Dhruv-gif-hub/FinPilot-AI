from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path

from ..core.dependencies import require_read_user
from ..services.report.ReportService import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"],)

@router.get("/tasks/{task_id}")
async def list_reports(
    merchant_id: UUID,
    task_id = Path(),
    current_user=Depends(require_read_user)):

    return await ReportService.list_reports(
        user_id=current_user.id,
        merchant_id=merchant_id,
        task_id=task_id
    )


@router.get("/{report_id}")
async def get_report(
    merchant_id:UUID,
    report_id = Path(),
    current_user=Depends(require_read_user)):

    report = await ReportService.report(
        report_id=report_id,
        merchant_id=merchant_id,
        user_id=current_user.id,
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    return report
