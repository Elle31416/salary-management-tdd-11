# SalaryOS — Full-Stack Salary Management Platform

A production-grade HR compensation tool for 10,000 employees.

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2.0 |
| Database | SQLite (swap to Postgres for production) |
| Frontend | React 18 + Vite + Tailwind CSS + Recharts |
| Tests | Pytest + FastAPI TestClient |
| Seed | Faker · bulk insert via `execute()` |

## Features

- **CRUD** — Create, list, edit, delete employees
- **Paginated table** — 20/page, server-side search & filters (country, status)
- **5 insight endpoints** — salary by country, by title, distribution, headcount, top-paid
- **Animated dashboard** — KPI cards, bar charts, distribution chart, pie chart
- **TDD** — 20 tests covering all routes + edge cases

---

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run tests first (TDD)
pytest tests/ -v

# Seed 10,000 employees (< 1 second)
python seed.py

# Start API server
uvicorn app.__init__:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## API Endpoints

### Employees
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/employees` | List with pagination, search, filters |
| GET | `/api/employees/{id}` | Single employee |
| POST | `/api/employees` | Create (returns 201) |
| PUT | `/api/employees/{id}` | Partial update |
| DELETE | `/api/employees/{id}` | Delete (returns 204) |

**Query params for GET /employees:**
- `page`, `page_size` (default 1, 20)
- `search` — matches name, email, job_title
- `country`, `department`, `status` — exact filters

### Insights
| Path | Description |
|------|-------------|
| `/api/insights/summary` | KPI totals |
| `/api/insights/salary-by-country` | Min/max/avg/headcount per country |
| `/api/insights/salary-by-title` | Avg salary per title+country |
| `/api/insights/salary-distribution` | Bucket counts (0–30k, 30–60k, …) |
| `/api/insights/headcount-by-department` | Counts per dept per country |
| `/api/insights/top-paid-titles` | Top 10 highest avg salary titles |

---

## Project Structure

```
salary-mgmt/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # FastAPI app, CORS, router inclusion
│   │   ├── database.py          # SQLAlchemy engine + get_db dependency
│   │   ├── models/employee.py   # ORM model + EmploymentStatus enum
│   │   ├── schemas/employee.py  # Pydantic v2 request/response schemas
│   │   ├── routes/
│   │   │   ├── employees.py     # CRUD routes
│   │   │   └── insights.py      # 6 analytics routes
│   │   └── services/
│   │       └── employee_service.py  # Business logic, bulk insert
│   ├── tests/test_api.py        # 20 pytest tests
│   ├── seed.py                  # 10,000 employee bulk seed
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── lib/
    │   │   ├── api.js            # Axios API client
    │   │   └── utils.js          # Formatters, status color maps
    │   ├── components/
    │   │   └── EmployeeModal.jsx # Add/edit form modal
    │   ├── pages/
    │   │   ├── EmployeesPage.jsx # Table + pagination + delete confirm
    │   │   └── InsightsPage.jsx  # KPI cards + 4 charts
    │   ├── App.jsx               # Router + nav shell
    │   └── main.jsx              # React Query setup
    ├── index.html
    ├── vite.config.js
    └── tailwind.config.js
```

---

## Deployment

### Backend → Render.com
1. New Web Service → connect repo
2. Build command: `pip install -r backend/requirements.txt`
3. Start command: `uvicorn app.__init__:app --host 0.0.0.0 --port $PORT`
4. Root dir: `backend/`

### Frontend → Vercel
1. Import repo → set root to `frontend/`
2. Set env var `VITE_API_URL` to your Render URL
3. Update `vite.config.js` proxy to use env var

---

## Commit Sequence (TDD)

```
1. feat: project scaffold + DB model + database config
2. test: add employee returns 201 / feat: POST /employees
3. test: list employees pagination / feat: GET /employees
4. test: update employee partial / feat: PUT /employees
5. test: delete employee / feat: DELETE /employees
6. feat: salary-by-country insight endpoint
7. feat: salary-distribution insight endpoint
8. feat: top-paid-titles + headcount insights
9. feat: seed script 10k employees bulk insert
10. feat: React employees table + pagination
11. feat: add/edit employee modal
12. feat: insights dashboard with charts
13. deploy: Render backend + Vercel frontend
```
