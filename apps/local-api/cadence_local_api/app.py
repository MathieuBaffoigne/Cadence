from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cadence_local_api.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="Cadence Local API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    return app
