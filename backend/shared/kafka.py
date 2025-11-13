"""Kafka helpers for producer configuration."""
import json
from typing import Any, Callable, Optional

from kafka import KafkaProducer

from .config import settings


Serializer = Callable[[Any], bytes]


def _json_serializer(value: Any) -> bytes:
    return json.dumps(value).encode("utf-8")


def _string_serializer(value: Optional[str]) -> bytes:
    if value is None:
        return b""
    return value.encode("utf-8")


def create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers_list,
        security_protocol=settings.kafka_security_protocol,
        sasl_mechanism=settings.kafka_sasl_mechanism,
        sasl_plain_username=settings.kafka_sasl_username,
        sasl_plain_password=settings.kafka_sasl_password,
        value_serializer=_json_serializer,
        key_serializer=_string_serializer,
        linger_ms=5,
    )


__all__ = ["create_producer"]
