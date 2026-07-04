from fastapi import FastAPI

from cadence_local_api.app import create_app

app: FastAPI = create_app()
