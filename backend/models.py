from sqlalchemy import Column, String, Float, Integer, Date, DateTime, JSON, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base
import uuid

def gen_id():
    return str(uuid.uuid4())

class Patient(Base):
    __tablename__ = "patients"
    id = Column(String, primary_key=True, default=gen_id)
    cpf = Column(String, nullable=True, index=True)  # novo campo (unique via índice abaixo)
    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=True)
    height_m = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    imc = Column(Float, nullable=True)
    allergies = Column(JSON, default=list)
    meds = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    encounters = relationship("Encounter", back_populates="patient", cascade="all,delete")

class Encounter(Base):
    __tablename__ = "encounters"
    id = Column(String, primary_key=True, default=gen_id)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    data = Column(JSON, default=dict)         # respostas parciais
    suggestions = Column(JSON, default=dict)  # resumo/sugestões
    created_at = Column(DateTime, server_default=func.now())
    patient = relationship("Patient", back_populates="encounters")
