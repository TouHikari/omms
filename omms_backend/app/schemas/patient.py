from typing import List, Optional
from pydantic import BaseModel

class PatientOut(BaseModel):
    patientId: int
    userId: Optional[int] = None
    name: str
    gender: Optional[int] = None
    birthday: Optional[str] = None
    idCard: Optional[str] = None
    address: Optional[str] = None
    emergencyContact: Optional[str] = None
    emergencyPhone: Optional[str] = None

class PatientsListData(BaseModel):
    list: List[PatientOut]
    total: int
    page: int
    pageSize: int

class PatientsListResponse(BaseModel):
    code: int
    message: str
    data: PatientsListData

class PatientResponse(BaseModel):
    code: int
    message: str
    data: PatientOut