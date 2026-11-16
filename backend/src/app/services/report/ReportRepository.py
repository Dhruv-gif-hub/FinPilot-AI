from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.agent_reports import AgentReport
from ...models.agent_tasks import AgentTask
from ...schemas.agent import ReportDraft


class ReportRepository:

    @staticmethod
    async def get_by_task_and_version(
        session: AsyncSession,
        task_id: UUID,
        report_version: int,
    ):
        stmt = select(AgentReport).where(
            AgentReport.task_id == task_id,
            AgentReport.report_version == report_version,
        )

        result = await session.scalars(stmt)

        return result.first()
    
    @staticmethod
    async def get_next_version(
        session: AsyncSession,
        task_id: UUID,
    ) -> int:
        stmt = select(
            func.coalesce(
                func.max(AgentReport.report_version),
                0,
            ) + 1
        ).where(
            AgentReport.task_id == task_id
        )

        result = await session.scalars(stmt)

        return result.one()

    @staticmethod
    async def create(
        session: AsyncSession,
        **kwargs,
    ) -> AgentReport:

        report = AgentReport(**kwargs)

        session.add(report)

        await session.flush()

        return report

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        report_id: UUID,
    ):
        stmt = select(AgentReport).where(
            AgentReport.id == report_id
        )

        result = await session.scalars(stmt)

        return result.first()

    @staticmethod
    async def list_by_task(
        session: AsyncSession,
        task_id: UUID,
    ):
        stmt = (
            select(AgentReport)
            .where(AgentReport.task_id == task_id)
            .order_by(AgentReport.report_version.desc())
        )

        result = await session.scalars(stmt)

        return result.all()

    @staticmethod
    async def _validate_task(
        session: AsyncSession,
        task_id: UUID,
        user_id: UUID,
        merchant_id: UUID,
    ):
        """
        Verify that the task belongs to the user
        and the requested merchant.
        """

        stmt = select(AgentTask).where(
            AgentTask.id == task_id,
            AgentTask.user_id == user_id,
            AgentTask.merchant_id == merchant_id,
        )

        result = await session.scalars(stmt)

        task = result.first()

        if task is None:
            raise PermissionError(
                "Task not found or access denied."
            )

        return task

    @staticmethod
    def _validate_evidence(
        report: ReportDraft,
    ) -> None:
        """
        Validate internal consistency of evidence references.
        """

        evidence_ids = {doc_id 
            for item in report.evidence 
            for doc_id in item.document_id
            }

        chunk_ids = {chunk_id 
            for item in report.evidence 
            for chunk_id in item.chunk_id
            }

        for finding in report.findings:

            for evidence_id in finding.evidence_ids:

                if evidence_id.startswith("metric:"):
                    continue

                if evidence_id not in evidence_ids and evidence_id not in chunk_ids:
                    raise ValueError(
                        f"Unknown evidence reference: "
                        f"{evidence_id}"
                    )

    @staticmethod
    async def save_report(
        session: AsyncSession,
        task_id: UUID,
        user_id: UUID,
        merchant_id: UUID,
        report_data: dict,
        report_version: int | None = None,
    ) -> UUID:
        """
        Validate and persist an agent report.

        If a version is supplied, retries reuse that version.
        If omitted, a new version is allocated.
        """

        # 1. Validate the Pydantic report.
        try:
            report = ReportDraft.model_validate(
                report_data
            )
        except ValidationError as exc:
            raise ValueError(
                f"Invalid report structure: {exc}"
            ) from exc

        # 2. Validate evidence references.
        ReportRepository._validate_evidence(report)

        async with session.begin():

            # 3. Verify task ownership.
            await ReportRepository._validate_task(
                session=session,
                task_id=task_id,
                user_id=user_id,
                merchant_id=merchant_id,
            )

            # 4. Determine report version.
            if report_version is None:
                report_version = (
                    await ReportRepository.get_next_version(
                        session,
                        task_id,
                    )
                )

            if report_version < 1:
                raise ValueError(
                    "Report version must be positive."
                )

            # 5. Check whether this report version
            # already exists.
            existing = (
                await ReportRepository.get_by_task_and_version(
                    session,
                    task_id,
                    report_version,
                )
            )

            if existing is not None:

                # Do not overwrite an existing report
                # silently during a Celery retry.
                return existing.id

            # 6. Insert the report.
            saved_report = (
                await ReportRepository.create(
                    session,
                    task_id=task_id,
                    report_version=report_version,
                    title=report.title,
                    content=report.model_dump(mode="json"),
                    evidence=report.evidence,
                    summary=report.summary,
                    status="COMPLETED",
                )
            )

            return saved_report.id

    @staticmethod
    async def get_report(
        session: AsyncSession,
        report_id: UUID,
        user_id: UUID,
        merchant_id: UUID,
    ):
        
        stmt = (
            select(AgentReport)
            .join(
                AgentTask,
                AgentTask.id == AgentReport.task_id,
            )
            .where(
                AgentReport.id == report_id,
                AgentTask.user_id == user_id,
                AgentTask.merchant_id == merchant_id,
            )
        )

        result = await session.scalars(stmt)

        report = result.first()

        if report is None:
            raise LookupError(
                "Report not found or access denied."
            )

        return report

    @staticmethod
    async def list_reports(
        session: AsyncSession,
        *,
        task_id: UUID,
        user_id: UUID,
        merchant_id: UUID,
    ):
        await ReportRepository._validate_task(
            session,
            task_id,
            user_id,
            merchant_id,
        )

        return await ReportRepository.list_by_task(
            session,
            task_id,
        )
