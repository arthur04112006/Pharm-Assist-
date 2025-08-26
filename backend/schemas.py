from pydantic import BaseModel, StringConstraints, confloat
from typing import List, Optional
from typing_extensions import Annotated
from datetime import date

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
CPF = Annotated[str, StringConstraints(pattern=r"^\d{11}$")]  # somente 11 dígitos

class Med(BaseModel):
    nome: str
    dose: Optional[str] = None

class PatientIn(BaseModel):
    name: Name
    cpf: CPF  # novo: obrigatório no cadastro
    birth_date: Optional[date] = None
    height_m: Optional[confloat(ge=0.5, le=2.3)] = None
    weight_kg: Optional[confloat(ge=2, le=350)] = None
    allergies: List[str] = []
    meds: List[Med] = []

class EncounterIn(BaseModel):
    data: dict

class EncounterOut(BaseModel):
    id: str
    patient_id: str
    data: dict
    suggestions: dict
