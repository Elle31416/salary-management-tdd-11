from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import employees, insights

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Salary Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
