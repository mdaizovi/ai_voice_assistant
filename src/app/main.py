from fastapi import FastAPI

from api.api import api_router

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router)
    return app

app = create_app()
