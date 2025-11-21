from __future__ import annotations

from typing import Generator
from sqlalchemy.orm import Session

from .database import get_db
from .security import get_api_key


# Dependency wrappers for clarity/consistency

def db_session() -> Generator[Session, None, None]:
    yield from get_db()


def api_key_dep() -> str:
    return get_api_key()  # simply re-expose for import convenience
