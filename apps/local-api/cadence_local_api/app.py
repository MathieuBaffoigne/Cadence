from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cadence_local_api.api.routers.employee_routes import router as employee_router
from cadence_local_api.api.routers.health_routes import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="Cadence Local API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(employee_router)

    return app
