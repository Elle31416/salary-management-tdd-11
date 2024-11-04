from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from fastapi import HTTPException


def get_employees(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    country: str | None = None,
    department: str | None = None,
    status: str | None = None,
):
    q = db.query(Employee)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Employee.name.ilike(like), Employee.email.ilike(like), Employee.job_title.ilike(like)))
    if country:
        q = q.filter(Employee.country == country)
    if department:
        q = q.filter(Employee.department == department)
    if status:
        q = q.filter(Employee.employment_status == status)

    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def get_employee(db: Session, employee_id: int) -> Employee:
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


def create_employee(db: Session, data: EmployeeCreate) -> Employee:
    existing = db.query(Employee).filter(Employee.email == data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    emp = Employee(**data.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


def update_employee(db: Session, employee_id: int, data: EmployeeUpdate) -> Employee:
    emp = get_employee(db, employee_id)
    updates = data.model_dump(exclude_unset=True)
    if "email" in updates and updates["email"] != emp.email:
        conflict = db.query(Employee).filter(Employee.email == updates["email"]).first()
        if conflict:
            raise HTTPException(status_code=409, detail="Email already registered")
    for key, value in updates.items():
        setattr(emp, key, value)
    db.commit()
    db.refresh(emp)
    return emp


def delete_employee(db: Session, employee_id: int):
    emp = get_employee(db, employee_id)
    db.delete(emp)
    db.commit()


def bulk_insert(db: Session, records: list[dict]):
    db.execute(Employee.__table__.insert(), records)
    db.commit()
