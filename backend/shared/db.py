"""Database utilities shared across services."""
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import Column, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import settings

engine = create_engine(settings.db_dsn, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String, primary_key=True, index=True)
    value = Column(Text, nullable=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_resource_from_db(resource_id: str) -> Optional[str]:
    with get_session() as session:
        resource = session.get(Resource, resource_id)
        return resource.value if resource else None


def upsert_resource_to_db(resource_id: str, value: str) -> None:
    with get_session() as session:
        resource = session.get(Resource, resource_id)
        if resource:
            resource.value = value
        else:
            session.add(Resource(id=resource_id, value=value))


__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "Resource",
    "init_db",
    "get_session",
    "get_resource_from_db",
    "upsert_resource_to_db",
]
