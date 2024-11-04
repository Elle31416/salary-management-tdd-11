from sqlalchemy import Column, Integer, String, Float, Date, Enum as SAEnum
from app.database import Base
import enum


class EmploymentStatus(str, enum.Enum):
    active = "active"
    on_leave = "on_leave"
    terminated = "terminated"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    job_title = Column(String, nullable=False, index=True)
    department = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False, index=True)
    salary = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    employment_status = Column(SAEnum(EmploymentStatus), nullable=False, default=EmploymentStatus.active)
    hire_date = Column(Date, nullable=False)
