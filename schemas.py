# schemas.py
# Pydantic models for request/response validation. This enforces the
# assessment's validation rules at the API layer (server-side).
from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional
from enum import Enum

class SexEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"
    decline = "Decline to Answer"

class PatientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    sex: SexEnum
    phone_number: str = Field(..., pattern=r"^\d{10}$")  # US 10-digit
    email: Optional[EmailStr] = None
    address_line_1: str = Field(..., min_length=1)
    address_line_2: Optional[str] = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")  # ZIP or ZIP+4
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: str = "English"
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = Field(None, pattern=r"^\d{10}$")

    @field_validator("date_of_birth")
    def dob_not_future(cls, v):
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v

class PatientResponse(PatientCreate):
    patient_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True

class Envelope(BaseModel):
    """Consistent response envelope: {"data": {...}, "error": null}"""
    data: Optional[dict | list] = None
    error: Optional[str] = None