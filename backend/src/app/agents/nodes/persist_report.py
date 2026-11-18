from uuid import UUID

from ...services.report.ReportService import ReportService


async def persist_report_node(state, runtime):

    context = runtime.context

    report_id = await ReportService.Save_report(
        task_id=UUID(state["task_id"]),
        user_id=context.user_id,
        merchant_id=context.merchant_id,
        report_data=state["final_report"],
        report_version=1,
    )

    return {
        "report_id": str(report_id),
        "status": "completed",
        "result": state["final_report"]
    }