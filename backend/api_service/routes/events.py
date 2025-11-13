"""Event ingestion endpoints."""
import logging
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from shared.auth import User, require_roles
from shared.config import settings
from shared.kafka import create_producer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["events"])
producer = create_producer()


class EventIn(BaseModel):
    device_id: str = Field(..., min_length=1)
    payload: Dict[str, Any]


class EventAck(BaseModel):
    request_id: str
    status: str = "accepted"


@router.post("/events", status_code=status.HTTP_202_ACCEPTED, response_model=EventAck)
async def publish_event(
    event: EventIn,
    user: User = Depends(require_roles("device", "admin")),
) -> EventAck:
    request_id = str(uuid4())
    message = {
        "request_id": request_id,
        "device_id": event.device_id,
        "payload": event.payload,
        "user_id": user.sub,
        "received_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        future = producer.send(
            settings.kafka_events_topic,
            key=event.device_id,
            value=message,
        )
        future.get(timeout=10)
    except Exception as exc:  # pragma: no cover - integration heavy
        logger.exception(
            "Failed to publish event",
            extra={
                "extra_fields": {
                    "device_id": event.device_id,
                    "request_id": request_id,
                }
            },
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to queue event",
        ) from exc

    logger.info(
        "Event accepted",
        extra={"extra_fields": {"request_id": request_id, "device_id": event.device_id}},
    )
    return EventAck(request_id=request_id)
