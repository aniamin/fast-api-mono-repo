"""Entrypoint for the FastAPI service."""
import logging

from fastapi import FastAPI

from shared.db import init_db
from shared.logging import configure_logging

from .routes import events, resources

logger = logging.getLogger(__name__)

app = FastAPI(title="Events Backend API", version="1.0.0")
app.include_router(resources.router)
app.include_router(events.router)


@app.on_event("startup")
async def on_startup() -> None:
    configure_logging()
    init_db()
    logger.info("API service startup complete")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("API service shutdown")


__all__ = ["app"]
