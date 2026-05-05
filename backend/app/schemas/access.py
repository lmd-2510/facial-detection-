from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


AccessDecision = Literal["granted", "denied", "error"]


class AccessCheckRequest(BaseModel):
    camera_id: int
    image_path: str = Field(min_length=1)


class AccessCheckResponse(BaseModel):
    log_id: int
    status: AccessDecision
    employee_id: int | None
    camera_id: int
    score: float | None
    image_path: str
    message: str
    created_at: datetime
