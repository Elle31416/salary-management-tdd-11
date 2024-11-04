"""RED: insight endpoints — written before routes exist."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.__init__ import app

TEST_DB_URL = "sqlite:///./test_insights.db"
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

A = {"name": "Alice", "email": "alice@x.com", "job_title": "Software Engineer",
     "department": "Engineering", "country": "USA", "salary": 120000,
     "currency": "USD", "employment_status": "active", "hire_date": "2022-01-01"}
B = {**A, "email": "bob@x.com", "name": "Bob", "country": "UK",
     "salary": 80000, "currency": "GBP", "department": "Sales",
     "job_title": "Account Executive"}

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield

def test_summary_returns_correct_totals():
    client.post("/api/employees", json=A)
    client.post("/api/employees", json=B)
    r = client.get("/api/insights/summary")
    assert r.status_code == 200
    d = r.json()
    assert d["total_employees"] == 2
    assert d["active_employees"] == 2
    assert d["countries"] == 2
    assert d["departments"] == 2

def test_salary_by_country_contains_both_countries():
    client.post("/api/employees", json=A)
    client.post("/api/employees", json=B)
    r = client.get("/api/insights/salary-by-country")
    countries = {row["country"] for row in r.json()}
    assert "USA" in countries and "UK" in countries

def test_salary_distribution_has_correct_buckets():
    client.post("/api/employees", json=A)
    client.post("/api/employees", json=B)
    r = client.get("/api/insights/salary-distribution")
    buckets = {b["bucket"]: b["count"] for b in r.json()}
    assert buckets.get("60k-100k", 0) == 1   # Bob: 80k
    assert buckets.get("100k-150k", 0) == 1  # Alice: 120k

def test_top_paid_titles_sorted_descending():
    client.post("/api/employees", json=A)
    client.post("/api/employees", json=B)
    r = client.get("/api/insights/top-paid-titles")
    salaries = [row["avg_salary"] for row in r.json()]
    assert salaries == sorted(salaries, reverse=True)

def test_headcount_by_department_groups_correctly():
    client.post("/api/employees", json=A)
    client.post("/api/employees", json=B)
    r = client.get("/api/insights/headcount-by-department")
    depts = {row["department"] for row in r.json()}
    assert "Engineering" in depts and "Sales" in depts
