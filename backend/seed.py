"""Seed the database with 10,000 fake employees using a single bulk insert."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from datetime import date
import random
from app.database import engine, Base, SessionLocal
from app.models.employee import Employee, EmploymentStatus

fake = Faker()

COUNTRIES = ["USA", "UK", "Germany", "Canada", "Australia", "India", "France", "Brazil", "Japan", "Netherlands"]
DEPARTMENTS = ["Engineering", "Sales", "Marketing", "Finance", "HR", "Operations", "Legal", "Product", "Design", "Support"]
JOB_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Staff Engineer", "Principal Engineer",
    "Product Manager", "Senior Product Manager", "Director of Product",
    "Data Scientist", "Data Analyst", "ML Engineer",
    "Sales Manager", "Account Executive", "Sales Director",
    "Marketing Manager", "Content Strategist", "Growth Manager",
    "HR Manager", "HR Business Partner", "Recruiter",
    "Finance Analyst", "Senior Finance Analyst", "CFO",
    "UX Designer", "UI Designer", "Design Lead",
    "Operations Manager", "COO", "Business Analyst",
    "Legal Counsel", "Senior Legal Counsel",
    "Customer Support Specialist", "Support Lead",
]
SALARY_RANGES = {
    "Software Engineer": (70000, 130000),
    "Senior Software Engineer": (110000, 180000),
    "Staff Engineer": (160000, 240000),
    "Principal Engineer": (190000, 280000),
    "Product Manager": (90000, 150000),
    "Senior Product Manager": (130000, 200000),
    "Director of Product": (170000, 250000),
    "Data Scientist": (90000, 160000),
    "Data Analyst": (65000, 110000),
    "ML Engineer": (110000, 190000),
    "Sales Manager": (70000, 130000),
    "Account Executive": (55000, 110000),
    "Sales Director": (130000, 220000),
    "Marketing Manager": (65000, 120000),
    "Content Strategist": (55000, 95000),
    "Growth Manager": (75000, 140000),
    "HR Manager": (60000, 110000),
    "HR Business Partner": (70000, 120000),
    "Recruiter": (50000, 90000),
    "Finance Analyst": (60000, 110000),
    "Senior Finance Analyst": (80000, 140000),
    "CFO": (180000, 320000),
    "UX Designer": (70000, 130000),
    "UI Designer": (65000, 120000),
    "Design Lead": (110000, 180000),
    "Operations Manager": (65000, 120000),
    "COO": (170000, 300000),
    "Business Analyst": (60000, 110000),
    "Legal Counsel": (90000, 160000),
    "Senior Legal Counsel": (130000, 220000),
    "Customer Support Specialist": (40000, 70000),
    "Support Lead": (60000, 100000),
}
CURRENCY_BY_COUNTRY = {
    "USA": "USD", "UK": "GBP", "Germany": "EUR", "Canada": "CAD",
    "Australia": "AUD", "India": "INR", "France": "EUR", "Brazil": "BRL",
    "Japan": "JPY", "Netherlands": "EUR",
}
STATUSES = [EmploymentStatus.active] * 85 + [EmploymentStatus.on_leave] * 10 + [EmploymentStatus.terminated] * 5


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing
    db.query(Employee).delete()
    db.commit()

    emails_used = set()
    records = []
    for _ in range(10000):
        title = random.choice(JOB_TITLES)
        country = random.choice(COUNTRIES)
        low, high = SALARY_RANGES.get(title, (50000, 100000))
        salary = round(random.uniform(low, high), 2)
        email = fake.unique.email()
        hire_date = fake.date_between(start_date=date(2010, 1, 1), end_date=date.today())
        records.append({
            "name": fake.name(),
            "email": email,
            "job_title": title,
            "department": random.choice(DEPARTMENTS),
            "country": country,
            "salary": salary,
            "currency": CURRENCY_BY_COUNTRY[country],
            "employment_status": random.choice(STATUSES),
            "hire_date": hire_date,
        })

    db.execute(Employee.__table__.insert(), records)
    db.commit()
    db.close()
    print(f"✅ Seeded {len(records)} employees successfully.")


if __name__ == "__main__":
    main()
