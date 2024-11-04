"""RED: test GET /employees/{id} — found and not-found."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.__init__ import app

TEST_DB_URL = "sqlite:///./test_get.db"
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
    "country": "USA", "salary": 120000, "currency": "USD",
    "employment_status": "active", "hire_date": "2022-03-15",
}

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield

def test_get_employee_by_id_returns_correct_record():
    created = client.post("/api/employees", json=SAMPLE).json()
    r = client.get(f"/api/employees/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Alice Smith"
    assert r.json()["email"] == "alice@example.com"

def test_get_employee_not_found_returns_404():
    r = client.get("/api/employees/99999")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()
