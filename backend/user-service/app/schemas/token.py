"""Token-related Pydantic schemas."""

from typing import Optional

from pydantic import BaseModel


class TokenData(BaseModel):
    """Token data extracted from JWT."""

    user_id: int
    email: str
