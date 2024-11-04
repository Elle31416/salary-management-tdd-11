from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.models.employee import Employee

router = APIRouter()


@router.get("/salary-by-country")
def salary_by_country(db: Session = Depends(get_db)):
    rows = db.query(
        Employee.country,
        func.min(Employee.salary).label("min"),
        func.max(Employee.salary).label("max"),
        func.avg(Employee.salary).label("avg"),
        func.count(Employee.id).label("headcount"),
    ).group_by(Employee.country).all()
    return [
        {"country": r.country, "min": round(r.min, 2), "max": round(r.max, 2), "avg": round(r.avg, 2), "headcount": r.headcount}
        for r in rows
    ]


@router.get("/salary-by-title")
def salary_by_title(db: Session = Depends(get_db)):
    rows = db.query(
        Employee.job_title,
        Employee.country,
        func.avg(Employee.salary).label("avg"),
        func.count(Employee.id).label("headcount"),
    ).group_by(Employee.job_title, Employee.country).all()
    return [
        {"job_title": r.job_title, "country": r.country, "avg": round(r.avg, 2), "headcount": r.headcount}
        for r in rows
    ]


@router.get("/salary-distribution")
def salary_distribution(db: Session = Depends(get_db)):
    buckets = [
        ("0-30k", 0, 30000),
        ("30k-60k", 30000, 60000),
        ("60k-100k", 60000, 100000),
        ("100k-150k", 100000, 150000),
        ("150k+", 150000, 9999999),
    ]
    result = []
    for label, low, high in buckets:
        count = db.query(func.count(Employee.id)).filter(
            Employee.salary >= low, Employee.salary < high
        ).scalar()
        result.append({"bucket": label, "count": count})
    return result


@router.get("/headcount-by-department")
def headcount_by_department(db: Session = Depends(get_db)):
    rows = db.query(
        Employee.department,
        Employee.country,
        func.count(Employee.id).label("headcount"),
    ).group_by(Employee.department, Employee.country).all()
    return [{"department": r.department, "country": r.country, "headcount": r.headcount} for r in rows]


@router.get("/top-paid-titles")
def top_paid_titles(db: Session = Depends(get_db)):
    rows = db.query(
        Employee.job_title,
        func.avg(Employee.salary).label("avg_salary"),
        func.count(Employee.id).label("headcount"),
    ).group_by(Employee.job_title).order_by(func.avg(Employee.salary).desc()).limit(10).all()
    return [{"job_title": r.job_title, "avg_salary": round(r.avg_salary, 2), "headcount": r.headcount} for r in rows]


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    total = db.query(func.count(Employee.id)).scalar()
    avg_salary = db.query(func.avg(Employee.salary)).scalar() or 0
    active = db.query(func.count(Employee.id)).filter(Employee.employment_status == "active").scalar()
    countries = db.query(func.count(func.distinct(Employee.country))).scalar()
    departments = db.query(func.count(func.distinct(Employee.department))).scalar()
    return {
        "total_employees": total,
        "avg_salary": round(avg_salary, 2),
        "active_employees": active,
        "countries": countries,
        "departments": departments,
    }
