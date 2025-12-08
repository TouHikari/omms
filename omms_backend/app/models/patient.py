from typing import Optional
from datetime import datetime

from sqlalchemy import Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Patient(Base):
    """患者表模型"""
    __tablename__ = "patients"
    
    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    gender: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    birthday: Mapped[Optional[str]] = mapped_column(Date, nullable=True)
    id_card: Mapped[Optional[str]] = mapped_column(String(18), nullable=True, unique=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, onupdate=datetime.now())
    
    # 关系定义
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="patient")
    user: Mapped["User"] = relationship("User", back_populates="patient")