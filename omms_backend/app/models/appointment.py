from typing import Optional
from datetime import datetime

from sqlalchemy import Integer, String, Text, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Department(Base):
    """科室表模型"""
    __tablename__ = "departments"
    
    dept_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dept_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.now)
    
    # 关系定义
    doctors: Mapped[list["Doctor"]] = relationship("Doctor", back_populates="department")


class Doctor(Base):
    """医生表模型"""
    __tablename__ = "doctors"
    
    doctor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True, index=True)
    doctor_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.dept_id"), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    specialty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    introduction: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    available_status: Mapped[int] = mapped_column(Integer, default=1, index=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.now)
    
    # 关系定义
    department: Mapped["Department"] = relationship("Department", back_populates="doctors")
    schedules: Mapped[list["Schedule"]] = relationship("Schedule", back_populates="doctor")
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="doctor")


class Schedule(Base):
    """医生排班表模型"""
    __tablename__ = "doctor_schedules"
    
    schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctors.doctor_id"), nullable=False, index=True)
    work_date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime] = mapped_column(Time, nullable=False)
    max_appointments: Mapped[int] = mapped_column(Integer, default=20)
    booked: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1, index=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.now)
    
    # 关系定义
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedules")
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="schedule")


class Appointment(Base):
    """预约表模型"""
    __tablename__ = "appointments"
    
    appt_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patients.patient_id"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctors.doctor_id"), nullable=False, index=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctor_schedules.schedule_id"), nullable=False, index=True)
    appt_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    status: Mapped[int] = mapped_column(Integer, default=0, index=True)
    symptom_desc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, onupdate=datetime.now)
    
    # 关系定义
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")
    schedule: Mapped["Schedule"] = relationship("Schedule", back_populates="appointments")

