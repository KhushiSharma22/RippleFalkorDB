"""FastAPI app factory."""

from fastapi import FastAPI

from ripple.api.routes import graph, incidents, scenarios, stream


def create_app() -> FastAPI:
    app = FastAPI(title="Ripple")
    app.include_router(incidents.router)
    app.include_router(scenarios.router)
    app.include_router(graph.router)
    app.include_router(stream.router)
    return app


app = create_app()
