from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class MedicalRecord(Base):
    __tablename__ = "records"
    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    dept_id: Mapped[int] = mapped_column(Integer, index=True)
    doctor_id: Mapped[int] = mapped_column(Integer, index=True)
    patient_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    patient_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    created_at: Mapped[str] = mapped_column(String(19), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True, default="draft")
    template_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prescriptions_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    labs_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    imaging_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class RecordTemplate(Base):
    __tablename__ = "record_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    scope: Mapped[str] = mapped_column(String(50), index=True)
    fields_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    defaults_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
