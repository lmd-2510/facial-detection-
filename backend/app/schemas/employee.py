from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EmployeeStatus = Literal["active", "inactive"]


class EmployeeBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    department: str | None = Field(default=None, max_length=150)
    status: EmployeeStatus = "active"


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    department: str | None = Field(default=None, max_length=150)
    status: EmployeeStatus | None = None


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EmployeeEmbeddingJobRequest(BaseModel):
    image_path: str = Field(min_length=1, max_length=1000)


class EmployeeEmbeddingJobResponse(BaseModel):
    job_id: str
    type: str
    employee_id: int
    image_path: str
    queue_name: str
    message: str
