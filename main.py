# main.py
# The FastAPI application. Exposes the REST endpoints from the assessment
# and a tool endpoint that Vapi calls to save patient data.
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CareCloud Patient Registration API")

# ---------- Helper: standard envelope ----------
def envelope(data=None, error=None):
    return {"data": data, "error": error}

# ---------- CRUD Endpoints ----------

@app.get("/patients")
def list_patients(
    last_name: Optional[str] = Query(None),
    date_of_birth: Optional[date] = Query(None),
    phone_number: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List patients with optional filters. Soft-deleted records are excluded."""
    q = db.query(models.Patient).filter(models.Patient.deleted_at.is_(None))
    if last_name:
        q = q.filter(models.Patient.last_name == last_name)
    if date_of_birth:
        q = q.filter(models.Patient.date_of_birth == date_of_birth)
    if phone_number:
        q = q.filter(models.Patient.phone_number == phone_number)
    patients = q.all()
    return envelope(data=[schemas.PatientResponse.from_orm(p).dict() for p in patients])

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Retrieve a single patient by UUID. Returns 404 if not found or soft-deleted."""
    p = db.query(models.Patient).filter(
        models.Patient.patient_id == patient_id,
        models.Patient.deleted_at.is_(None)
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return envelope(data=schemas.PatientResponse.from_orm(p).dict())

@app.post("/patients", status_code=201)
def create_patient(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient. Validates all fields via Pydantic."""
    db_patient = models.Patient(**payload.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return envelope(data=schemas.PatientResponse.from_orm(db_patient).dict())

@app.put("/patients/{patient_id}")
def update_patient(
    patient_id: str,
    payload: schemas.PatientCreate,
    db: Session = Depends(get_db),
):
    """Partial updates are not strictly partial here—we replace the record.
    For the assessment's scope, this is acceptable and keeps the code simple."""
    p = db.query(models.Patient).filter(
        models.Patient.patient_id == patient_id,
        models.Patient.deleted_at.is_(None)
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(p, key, value)
    p.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(p)
    return envelope(data=schemas.PatientResponse.from_orm(p).dict())

@app.delete("/patients/{patient_id}", status_code=200)
def soft_delete_patient(patient_id: str, db: Session = Depends(get_db)):
    """Soft delete: set deleted_at timestamp. Do not hard-delete."""
    p = db.query(models.Patient).filter(
        models.Patient.patient_id == patient_id,
        models.Patient.deleted_at.is_(None)
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    p.deleted_at = datetime.utcnow()
    db.commit()
    return envelope(data={"message": "Patient soft-deleted"})

# ---------- Vapi Tool Endpoint ----------
# Vapi's LLM will call this endpoint via function calling to save the patient.
# The payload matches the PatientCreate schema exactly.
@app.post("/tools/save-patient")
def save_patient_tool(payload: schemas.PatientCreate, db: Session = Depends(get_db)):
    """
    This is the endpoint Vapi's function calling will hit.
    It behaves like POST /patients but returns a simpler message for the voice agent.
    """
    db_patient = models.Patient(**payload.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return {
        "status": "success",
        "patient_id": db_patient.patient_id,
        "message": f"Patient {db_patient.first_name} {db_patient.last_name} saved successfully."
    }

# ---------- Serve the Dashboard ----------
from fastapi.staticfiles import StaticFiles
import os

# Ensure the dashboard folder exists and mount it.
os.makedirs("dashboard", exist_ok=True)
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")