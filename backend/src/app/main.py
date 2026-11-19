from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore

from .agents.factory import create_finpilot_graph
from .api import agent_tasks, auth, document, merchants, reports, transaction
from .core.config import config_value
from .core.middleware.logging import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):

    # 1. Initialize PostgreSQL checkpointer.
    async with (AsyncPostgresSaver.from_conn_string(
        config_value.Database_url
    ) as checkpointer,
    AsyncPostgresStore.from_conn_string(
        config_value.Database_url) as store):

        # 2. Initialize checkpoint tables.
        await checkpointer.setup()
        await store.setup()

        # 3. Compile graph ONCE.
        app.state.graph = create_finpilot_graph(
            checkpointer=checkpointer,
            store=store
        )

        print("Graph initialized")

        # 4. Application starts accepting requests.
        yield

        # 5. Checkpointer and store connection closes automatically.

def create_app(lifespan) -> FastAPI:
    app = FastAPI(
        title="KnowBase-AI",
        description="AI Backend project",
        version="1.0.0",
        lifespan=lifespan
    )

    app.add_middleware(RequestLoggingMiddleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth.router, tags=["Auth"])
    app.include_router(document.router, tags=["Document RAG"])
    app.include_router(agent_tasks.router, tags=["Agent Tasks"])
    app.include_router(reports.router, tags=["Reports"])
    app.include_router(transaction.router, tags=["Transactions"])
    app.include_router(merchants.router, tags=["Merchants"])

    @app.get("/")
    def root():
        return {"message": "API is running"}

    return app

app = create_app(lifespan=lifespan)