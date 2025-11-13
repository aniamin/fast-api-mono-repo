"""Pydantic models shared by services."""
from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class ResourceModel(BaseModel):
    id: str
    value: str


class EventMessage(BaseModel):
    request_id: str
    device_id: str
    payload: Dict[str, Any]
    user_id: str
    received_at: datetime

