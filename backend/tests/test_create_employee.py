"""RED: test POST /employees before route exists."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.__init__ import app

TEST_DB_URL = "sqlite:///./test_create.db"
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

SAMPLE = {
    "name": "Alice Smith", "email": "alice@example.com",
    "job_title": "Software Engineer", "department": "Engineering",
    "country": "USA", "salary": 120000.00, "currency": "USD",
    "employment_status": "active", "hire_date": "2022-03-15",
}

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield

def test_create_employee_returns_201():
    r = client.post("/api/employees", json=SAMPLE)
    assert r.status_code == 201
    assert r.json()["id"] is not None

def test_create_employee_duplicate_email_returns_409():
    client.post("/api/employees", json=SAMPLE)
    r = client.post("/api/employees", json=SAMPLE)
    assert r.status_code == 409

def test_create_employee_negative_salary_returns_422():
    bad = {**SAMPLE, "salary": -1000, "email": "bad@example.com"}
    r = client.post("/api/employees", json=bad)
    assert r.status_code == 422
