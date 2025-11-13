"""Worker service entrypoint."""
import logging
import time
from typing import Any, Dict

from kafka.consumer.fetcher import ConsumerRecord

from shared.config import settings
from shared.logging import configure_logging

from .processor import create_consumer, create_dlq_producer, process_message

logger = logging.getLogger(__name__)
MAX_RETRIES = 3


def _send_to_dlq(dlq_producer, record: ConsumerRecord, error: Exception) -> None:
    payload: Dict[str, Any] = {
        "original": record.value,
        "device_id": record.key,
        "error": str(error),
    }
    dlq_producer.send(settings.kafka_dlq_topic, key=record.key, value=payload).get(timeout=10)
    logger.error(
        "Message sent to DLQ",
        extra={
            "extra_fields": {
                "topic": record.topic,
                "partition": record.partition,
                "offset": record.offset,
                "device_id": record.key,
            }
        },
    )


def _process_with_retry(record: ConsumerRecord, consumer, dlq_producer) -> None:
    attempt = 0
    while True:
        try:
            resource_id = process_message(record.value)
            logger.info(
                "Processed message",
                extra={
                    "extra_fields": {
                        "device_id": resource_id,
                        "topic": record.topic,
                        "partition": record.partition,
                        "offset": record.offset,
                    }
                },
            )
            consumer.commit()
            return
        except Exception as exc:  # pragma: no cover - integration heavy
            attempt += 1
            if attempt > MAX_RETRIES:
                _send_to_dlq(dlq_producer, record, exc)
                consumer.commit()
                return

            sleep_seconds = 2 ** attempt
            logger.warning(
                "Processing failed, retrying",
                extra={
                    "extra_fields": {
                        "attempt": attempt,
                        "sleep": sleep_seconds,
                        "error": str(exc),
                        "device_id": record.key,
                    }
                },
            )
            time.sleep(sleep_seconds)


def main() -> None:
    configure_logging()
    consumer = create_consumer()
    dlq_producer = create_dlq_producer()
    logger.info(
        "Worker service started",
        extra={"extra_fields": {"topic": settings.kafka_events_topic, "group": settings.kafka_group_id}},
    )

    try:
        for message in consumer:
            _process_with_retry(message, consumer, dlq_producer)
    except KeyboardInterrupt:
        logger.info("Worker interrupted")
    finally:
        consumer.close()
        dlq_producer.close()
        logger.info("Worker shutdown")


if __name__ == "__main__":
    main()
