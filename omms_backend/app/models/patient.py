from typing import Optional
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base

class Patient(Base):
    __tablename__ = "patients"
    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    gender: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    birthday: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    id_card: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)