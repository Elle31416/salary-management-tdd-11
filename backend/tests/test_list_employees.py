"""RED: test GET /employees pagination, search, and country filter."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.__init__ import app

TEST_DB_URL = "sqlite:///./test_list.db"
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

BASE = {
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

def test_list_employees_empty():
    r = client.get("/api/employees")
    assert r.status_code == 200
    assert r.json() == {"total": 0, "page": 1, "page_size": 20, "items": []}

def test_list_employees_pagination():
    for i in range(5):
        client.post("/api/employees", json={**BASE, "email": f"u{i}@x.com"})
    r = client.get("/api/employees?page=1&page_size=3")
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3

def test_list_employees_page_2():
    for i in range(5):
        client.post("/api/employees", json={**BASE, "email": f"u{i}@x.com"})
    r = client.get("/api/employees?page=2&page_size=3")
    assert len(r.json()["items"]) == 2

def test_list_employees_search_by_name():
    client.post("/api/employees", json=BASE)
    r = client.get("/api/employees?search=Alice")
    assert r.json()["total"] == 1

def test_list_employees_filter_by_country():
    client.post("/api/employees", json=BASE)
    client.post("/api/employees", json={**BASE, "email": "bob@x.com", "country": "UK"})
    assert client.get("/api/employees?country=USA").json()["total"] == 1
    assert client.get("/api/employees?country=UK").json()["total"] == 1
