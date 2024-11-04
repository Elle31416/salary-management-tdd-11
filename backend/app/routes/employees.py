from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeRead, PaginatedEmployees
from app.services import employee_service

router = APIRouter()


@router.get("", response_model=PaginatedEmployees)
def list_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    country: str | None = None,
    department: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    total, items = employee_service.get_employees(db, page, page_size, search, country, department, status)
    return PaginatedEmployees(total=total, page=page, page_size=page_size, items=items)


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return employee_service.get_employee(db, employee_id)


@router.post("", response_model=EmployeeRead, status_code=201)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db)):
    return employee_service.create_employee(db, data)


@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db)):
    return employee_service.update_employee(db, employee_id, data)


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee_service.delete_employee(db, employee_id)
