"""RED: test PUT /employees/{id} — partial update, not-found, email conflict."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.__init__ import app

TEST_DB_URL = "sqlite:///./test_update.db"
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

A = {
    "name": "Alice Smith", "email": "alice@example.com",
    "job_title": "Software Engineer", "department": "Engineering",
    "country": "USA", "salary": 120000, "currency": "USD",
    "employment_status": "active", "hire_date": "2022-03-15",
}
B = {**A, "email": "bob@example.com", "name": "Bob Jones"}

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield

def test_update_salary_only():
    emp = client.post("/api/employees", json=A).json()
    r = client.put(f"/api/employees/{emp['id']}", json={"salary": 150000})
    assert r.status_code == 200
    assert r.json()["salary"] == 150000
    assert r.json()["name"] == "Alice Smith"  # unchanged

def test_update_job_title():
    emp = client.post("/api/employees", json=A).json()
    r = client.put(f"/api/employees/{emp['id']}", json={"job_title": "Senior Software Engineer"})
    assert r.json()["job_title"] == "Senior Software Engineer"

def test_update_not_found_returns_404():
    r = client.put("/api/employees/99999", json={"salary": 100000})
    assert r.status_code == 404

def test_update_duplicate_email_returns_409():
    a = client.post("/api/employees", json=A).json()
    client.post("/api/employees", json=B)
    r = client.put(f"/api/employees/{a['id']}", json={"email": "bob@example.com"})
    assert r.status_code == 409
