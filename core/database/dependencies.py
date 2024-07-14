from typing import Generator
from core.database.config import SessionLocal


def get_database() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
