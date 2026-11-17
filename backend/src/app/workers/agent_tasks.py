import asyncio
from uuid import UUID

from app.agents.factory import create_finpilot_graph

from ..core.background_task.celery_setup import celery
from ..main import app
from ..services.task_execution.task_execution import ExecuteAgentTask

_worker_loop = None
_graph = app.state.graph


def get_worker_loop():

    global _worker_loop

    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()

        asyncio.set_event_loop(_worker_loop)

    return _worker_loop


def run_async(coroutine):

    loop = get_worker_loop()

    return loop.run_until_complete(coroutine)


def get_graph():

    global _graph

    if _graph is None:
        _graph = create_finpilot_graph(
            checkpointer=..., store=...
        )

    return _graph


async def execute_task_async(task_id: UUID):

    graph = get_graph()

    return await ExecuteAgentTask.execute(graph=graph, task_id=task_id)


@celery.task(
    bind=True,
    name="app.workers.agent_tasks.execute_agent_task",
    acks_late=True,
    max_retries=3,
)
def execute_agent_task(
    self,
    task_id: str,
):

    try:

        return run_async(
            execute_task_async(UUID(task_id))
        )

    except Exception as exc:

        raise self.retry(
            exc=exc,
            countdown=30 * (2 ** self.request.retries),
            max_retries=3,
        )
