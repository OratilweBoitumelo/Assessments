"""Test data for the end-to-end flow."""
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Employee:
    first_name: str
    middle_name: str
    last_name: str
    # Personal details
    nationality: str = "South African"
    marital_status: str = "Single"
    date_of_birth: date = date(1995, 5, 20)
    gender: str = "Male"
    # Job details
    joined_date: date = date(2025, 1, 11)
    job_title: str = "QA Engineer"
    job_category: str = "Professionals"
    sub_unit: str = "Quality Assurance"
    location: str | None = None  # None = pick any available location
    employment_status: str = "Full-Time Contract"

def new_employee() -> Employee:
    """Employee with a unique last name so every run is searchable/unambiguous."""
    suffix = datetime.now().strftime("%H%M%S")
    return Employee(first_name="Test", middle_name="Auto", last_name=f"Qa{suffix}")
