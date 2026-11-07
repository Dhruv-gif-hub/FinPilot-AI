from .ReportRepository import ReportRepository
from ...db.session import Session_local
from uuid import UUID

class ReportService:

    @staticmethod
    async def Save_report(
        task_id: UUID,
        user_id: UUID,
        merchant_id: UUID,
        report_data: dict,
        report_version: int | None = None,
    ):
        async with Session_local() as session:
            return await ReportRepository.save_report(
                session=session,
                task_id=task_id,
                user_id=user_id,
                merchant_id=merchant_id,
                report_data=report_data,
                report_version=report_version
            )