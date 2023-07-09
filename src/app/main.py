from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.api import api_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router)
    app.mount("/static", StaticFiles(directory="data/output"), name="static")
    return app


app = create_app()
