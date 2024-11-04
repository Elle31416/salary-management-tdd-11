"""Full test suite: CRUD operations + insights endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.__init__ import app

TEST_DB_URL = "sqlite:///./test_salary.db"
engine_test = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

Base.metadata.create_all(bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

SAMPLE_EMPLOYEE = {
    "name": "Alice Smith",
    "email": "alice@example.com",
    "job_title": "Software Engineer",
    "department": "Engineering",
    "country": "USA",
    "salary": 120000.00,
    "currency": "USD",
    "employment_status": "active",
    "hire_date": "2022-03-15",
}


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield


# --- Health ---
def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# --- POST /employees ---
def test_create_employee_returns_201():
    r = client.post("/api/employees", json=SAMPLE_EMPLOYEE)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == SAMPLE_EMPLOYEE["email"]
    assert data["id"] is not None


def test_create_employee_duplicate_email_returns_409():
    client.post("/api/employees", json=SAMPLE_EMPLOYEE)
    r = client.post("/api/employees", json=SAMPLE_EMPLOYEE)
    assert r.status_code == 409


def test_create_employee_negative_salary_returns_422():
    bad = {**SAMPLE_EMPLOYEE, "salary": -1000, "email": "bad@example.com"}
    r = client.post("/api/employees", json=bad)
    assert r.status_code == 422


# --- GET /employees ---
def test_list_employees_empty():
    r = client.get("/api/employees")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_list_employees_pagination():
    for i in range(5):
        emp = {**SAMPLE_EMPLOYEE, "email": f"user{i}@example.com"}
        client.post("/api/employees", json=emp)
    r = client.get("/api/employees?page=1&page_size=3")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3


def test_list_employees_search():
    client.post("/api/employees", json=SAMPLE_EMPLOYEE)
    r = client.get("/api/employees?search=Alice")
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_list_employees_filter_country():
    client.post("/api/employees", json=SAMPLE_EMPLOYEE)
    emp2 = {**SAMPLE_EMPLOYEE, "email": "bob@example.com", "country": "UK"}
    client.post("/api/employees", json=emp2)
    r = client.get("/api/employees?country=USA")
    assert r.json()["total"] == 1


# --- GET /employees/{id} ---
def test_get_employee_by_id():
    created = client.post("/api/employees", json=SAMPLE_EMPLOYEE).json()
    r = client.get(f"/api/employees/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Alice Smith"


def test_get_employee_not_found():
    r = client.get("/api/employees/99999")
    assert r.status_code == 404


# --- PUT /employees/{id} ---
def test_update_employee():
    created = client.post("/api/employees", json=SAMPLE_EMPLOYEE).json()
    r = client.put(f"/api/employees/{created['id']}", json={"salary": 150000})
    assert r.status_code == 200
    assert r.json()["salary"] == 150000


def test_update_employee_partial():
    created = client.post("/api/employees", json=SAMPLE_EMPLOYEE).json()
    r = client.put(f"/api/employees/{created['id']}", json={"job_title": "Senior Software Engineer"})
    assert r.status_code == 200
    assert r.json()["job_title"] == "Senior Software Engineer"
    assert r.json()["name"] == "Alice Smith"  # unchanged


def test_update_employee_not_found():
    r = client.put("/api/employees/99999", json={"salary": 100000})
    assert r.status_code == 404


# --- DELETE /employees/{id} ---
def test_delete_employee():
    created = client.post("/api/employees", json=SAMPLE_EMPLOYEE).json()
    r = client.delete(f"/api/employees/{created['id']}")
    assert r.status_code == 204
    r2 = client.get(f"/api/employees/{created['id']}")
    assert r2.status_code == 404


def test_delete_employee_not_found():
    r = client.delete("/api/employees/99999")
    assert r.status_code == 404


# --- Insights ---
def _seed_two_employees():
    client.post("/api/employees", json=SAMPLE_EMPLOYEE)
    emp2 = {**SAMPLE_EMPLOYEE, "email": "bob@example.com", "name": "Bob Jones",
            "country": "UK", "salary": 80000, "currency": "GBP", "department": "Sales",
            "job_title": "Account Executive"}
    client.post("/api/employees", json=emp2)


def test_insights_summary():
    _seed_two_employees()
    r = client.get("/api/insights/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["total_employees"] == 2
    assert data["countries"] == 2


def test_insights_salary_by_country():
    _seed_two_employees()
    r = client.get("/api/insights/salary-by-country")
    assert r.status_code == 200
    countries = {row["country"] for row in r.json()}
    assert "USA" in countries
    assert "UK" in countries


def test_insights_salary_by_title():
    _seed_two_employees()
    r = client.get("/api/insights/salary-by-title")
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_insights_salary_distribution():
    _seed_two_employees()
    r = client.get("/api/insights/salary-distribution")
    assert r.status_code == 200
    buckets = {b["bucket"]: b["count"] for b in r.json()}
    assert "60k-100k" in buckets
    assert "100k-150k" in buckets


def test_insights_headcount_by_department():
    _seed_two_employees()
    r = client.get("/api/insights/headcount-by-department")
    assert r.status_code == 200
    depts = {row["department"] for row in r.json()}
    assert "Engineering" in depts
    assert "Sales" in depts


def test_insights_top_paid_titles():
    _seed_two_employees()
    r = client.get("/api/insights/top-paid-titles")
    assert r.status_code == 200
    assert r.json()[0]["avg_salary"] >= r.json()[-1]["avg_salary"]
