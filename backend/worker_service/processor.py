"""Worker utilities for consuming and processing events."""
import json
from typing import Any, Dict, Optional

from kafka import KafkaConsumer, KafkaProducer

from shared.cache import invalidate_resource
from shared.config import settings
from shared.db import upsert_resource_to_db


JsonDict = Dict[str, Any]


def _json_deserializer(value: Optional[bytes]) -> JsonDict:
    if value is None:
        return {}
    return json.loads(value.decode("utf-8"))


def _string_deserializer(value: Optional[bytes]) -> Optional[str]:
    if value is None:
        return None
    return value.decode("utf-8")


def _json_serializer(value: Any) -> bytes:
    return json.dumps(value).encode("utf-8")


def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        settings.kafka_events_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers_list,
        group_id=settings.kafka_group_id,
        security_protocol=settings.kafka_security_protocol,
        sasl_mechanism=settings.kafka_sasl_mechanism,
        sasl_plain_username=settings.kafka_sasl_username,
        sasl_plain_password=settings.kafka_sasl_password,
        enable_auto_commit=False,
        value_deserializer=_json_deserializer,
        key_deserializer=_string_deserializer,
        auto_offset_reset="earliest",
    )


def create_dlq_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers_list,
        security_protocol=settings.kafka_security_protocol,
        sasl_mechanism=settings.kafka_sasl_mechanism,
        sasl_plain_username=settings.kafka_sasl_username,
        sasl_plain_password=settings.kafka_sasl_password,
        value_serializer=_json_serializer,
        key_serializer=lambda value: value.encode("utf-8") if value else b"",
    )


def process_message(value: JsonDict) -> str:
    device_id = value.get("device_id")
    payload = value.get("payload")

    if not device_id:
        raise ValueError("device_id missing from message")
    if payload is None:
        raise ValueError("payload missing from message")

    serialized_payload = json.dumps(payload)
    upsert_resource_to_db(device_id, serialized_payload)
    invalidate_resource(device_id)

    return device_id
