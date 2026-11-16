from fastapi import FastAPI

from .api import agent_tasks, auth, document, reports
from .core.middleware.logging import RequestLoggingMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="KnowBase-AI",
        description="AI Backend project",
        version="1.0.0"
    )

    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(auth.router, tags=["Auth"])
    app.include_router(document.router, tags=["Document RAG"])
    app.include_router(agent_tasks.router, tags=["Agent Tasks"])
    app.include_router(reports.router, tags=["Reports"])

    @app.get("/")
    def root():
        return {"message": "API is running"}

    return app

app = create_app()