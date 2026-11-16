from uuid import UUID
from ...db.session import Session_local
from .ReportRepository import ReportRepository


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

    @staticmethod
    async def list_reports(
        *,
        task_id: UUID,
        user_id: UUID,
        merchant_id: UUID,
    ):
        async with Session_local() as session:
            return await ReportRepository.list_reports(
                session=session,
                task_id=task_id,
                user_id=user_id,
                merchant_id=merchant_id
            )

    @staticmethod
    async def report(
        report_id: UUID,
        user_id: UUID,
        merchant_id: UUID,
    ):
        async with Session_local() as session:
            return await ReportRepository.get_report(
                session=session,
                report_id=report_id,
                user_id=user_id,
                merchant_id=merchant_id
            )
        