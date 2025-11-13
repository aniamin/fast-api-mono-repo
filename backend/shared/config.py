"""Application configuration shared across services."""
from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")

    db_dsn: str = Field(
        "postgresql+psycopg2://user:password@postgres:5432/appdb", env="DB_DSN"
    )
    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")

    kafka_bootstrap_servers: str = Field(
        "localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS"
    )
    kafka_events_topic: str = Field("events-input", env="KAFKA_EVENTS_TOPIC")
    kafka_dlq_topic: str = Field("events-dlq", env="KAFKA_DLQ_TOPIC")
    kafka_group_id: str = Field("events-processor", env="KAFKA_GROUP_ID")
    kafka_security_protocol: str = Field(
        "SASL_SSL", env="KAFKA_SECURITY_PROTOCOL"
    )
    kafka_sasl_mechanism: str = Field("PLAIN", env="KAFKA_SASL_MECHANISM")
    kafka_sasl_username: str = Field("", env="KAFKA_SASL_USERNAME")
    kafka_sasl_password: str = Field("", env="KAFKA_SASL_PASSWORD")

    jwt_secret: str = Field("super-secret", env="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def kafka_bootstrap_servers_list(self) -> List[str]:
        return [server.strip() for server in self.kafka_bootstrap_servers.split(",") if server.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
