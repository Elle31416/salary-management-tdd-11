"""RED: test DELETE /employees/{id} — success 204, gone 404, not-found 404."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.__init__ import app

TEST_DB_URL = "sqlite:///./test_delete.db"
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

def test_delete_employee_returns_204():
    emp = client.post("/api/employees", json=SAMPLE).json()
    r = client.delete(f"/api/employees/{emp['id']}")
    assert r.status_code == 204
    assert r.content == b""

def test_deleted_employee_no_longer_fetchable():
    emp = client.post("/api/employees", json=SAMPLE).json()
    client.delete(f"/api/employees/{emp['id']}")
    r = client.get(f"/api/employees/{emp['id']}")
    assert r.status_code == 404

def test_delete_nonexistent_returns_404():
    r = client.delete("/api/employees/99999")
    assert r.status_code == 404
