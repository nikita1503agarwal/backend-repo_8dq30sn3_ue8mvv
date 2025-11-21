from __future__ import annotations

import os
from fastapi import Header, HTTPException, status

DEFAULT_API_KEY = "secret123"


def get_api_key(x_api_key: str | None = Header(default=None, alias="X-API-KEY")) -> str:
    expected = os.getenv("API_KEY", DEFAULT_API_KEY)
    if x_api_key is None or x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return x_api_key
