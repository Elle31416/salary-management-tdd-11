from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional
from app.models.employee import EmploymentStatus


class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=3, max_length=200)
    job_title: str = Field(..., min_length=1, max_length=100)
    department: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    salary: float = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    employment_status: EmploymentStatus = EmploymentStatus.active
    hire_date: date


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = Field(None, min_length=3, max_length=200)
    job_title: Optional[str] = None
    department: Optional[str] = None
    country: Optional[str] = None
    salary: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    employment_status: Optional[EmploymentStatus] = None
    hire_date: Optional[date] = None


class EmployeeRead(EmployeeBase):
    id: int

    model_config = {"from_attributes": True}


class PaginatedEmployees(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[EmployeeRead]
