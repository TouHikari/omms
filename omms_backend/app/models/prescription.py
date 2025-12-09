from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base


class Prescription(Base):
    __tablename__ = "pharmacy_prescriptions"

    id = Column(String(32), primary_key=True)
    patient = Column(String(50), nullable=False)
    department = Column(String(50), nullable=False)
    doctor = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), nullable=False, default="pending")

    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prescription_id = Column(String(32), ForeignKey("pharmacy_prescriptions.id"), nullable=False, index=True)
    medicine_id = Column(BigInteger, ForeignKey("medicines.medicine_id"), nullable=False)
    name = Column(String(100), nullable=True)
    qty = Column(Integer, nullable=False, default=1)
    unit = Column(String(20), nullable=True)
    price = Column(Float, nullable=False, default=0.0)

    prescription = relationship("Prescription", back_populates="items")
