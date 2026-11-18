from uuid import UUID

from ...agents.context import FinPilotContext
from ..agent_run.agent_run_service import AgentRunService


class ExecuteAgentTask:

    @staticmethod
    async def execute(
        graph,
        task_id: UUID,
    ) -> dict | None:

        # 1. Claim task and create an AgentRun.
        execution = await AgentRunService.start(
            task_id
        )

        # None means completed/cancelled or already
        # being executed by another worker.
        if execution is None:
            return None

        run_id = execution["run_id"]

        try:

            # 2. Build trusted runtime context.
            context = FinPilotContext(
                user_id=execution["user_id"],
                merchant_id=execution["merchant_id"]
            )

            # 3. Build initial graph state.
            #
            # Put untrusted input first, then overwrite
            # reserved values with database values.
            initial_state = {
                **(execution["input_data"] or {}),
                "task_id": str(execution["task_id"]),
                "run_id": str(run_id),
                "task_type": execution["task_type"],
                "request": execution["prompt"]
            }

            # 4. Execute your existing graph.
            #
            # Same thread ID for the logical task.
            # AgentRun IDs still distinguish attempts.
            config = {
                "configurable": {
                    "thread_id": str(execution["task_id"]),
                }
            }

            graph_result = await graph.ainvoke(
                initial_state,
                config=config,
                context=context,
            )

            # 5. Finalize execution.
            await AgentRunService.complete(
                task_id=execution["task_id"],
                run_id=run_id,
                result=graph_result,
            )

            return graph_result

        except Exception as exc:

            await AgentRunService.fail(
                task_id=execution["task_id"],
                run_id=run_id,
                error=str(exc),
                retryable=False,
            )

            raise