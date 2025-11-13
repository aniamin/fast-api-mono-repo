"""Resource endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from shared.auth import User, require_roles
from shared.cache import get_cached_resource, set_cached_resource
from shared.db import get_resource_from_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["resources"])


class ResourceResponse(BaseModel):
    id: str
    value: str


@router.get("/resource/{resource_id}", response_model=ResourceResponse)
async def read_resource(
    resource_id: str,
    user: User = Depends(require_roles("user", "admin", "device")),
) -> ResourceResponse:
    cached = get_cached_resource(resource_id)
    if cached is not None:
        logger.debug(
            "Cache hit", extra={"extra_fields": {"resource_id": resource_id, "cache": "hit"}}
        )
        return ResourceResponse(id=resource_id, value=cached)

    logger.debug(
        "Cache miss", extra={"extra_fields": {"resource_id": resource_id, "cache": "miss"}}
    )
    value = get_resource_from_db(resource_id)
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    set_cached_resource(resource_id, value)
    logger.info(
        "Resource loaded from DB",
        extra={"extra_fields": {"resource_id": resource_id, "cache": "prime"}},
    )
    return ResourceResponse(id=resource_id, value=value)
