from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, engine
from .routes import router


# Create database tables
Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title=settings.app_name,
    description=(
        "FitBuddy AI Fitness Plan Generator "
        "using FastAPI, SQLite and Gemini."
    ),
    version="1.0.0"
)


app.mount(
    "/static",
    StaticFiles(directory="app/templates/static"),
    name="static"
)


app.include_router(
    router
)


@app.get(
    "/health",
    tags=["system"]
)
def health():

    return {
        "status": "ok",
        "app": settings.app_name
    }