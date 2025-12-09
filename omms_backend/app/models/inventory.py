from sqlalchemy import Column, Integer, BigInteger, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base


class InventoryBatch(Base):
    __tablename__ = "inventory_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(BigInteger, ForeignKey("medicines.medicine_id"), nullable=False, index=True)
    batch_no = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    received_at = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    medicine = relationship("Medicine")


class InventoryLog(Base):
    __tablename__ = "inventory_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(8), nullable=False)  # 'in' | 'out'
    medicine_id = Column(BigInteger, ForeignKey("medicines.medicine_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
    time = Column(DateTime, default=datetime.now)
    note = Column(String(255), nullable=True)
    batch_no = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    medicine = relationship("Medicine")


class MedicineStock(Base):
    __tablename__ = "medicine_stocks"

    stock_id = Column(BigInteger, primary_key=True, autoincrement=True)
    medicine_id = Column(BigInteger, ForeignKey("medicines.medicine_id"), nullable=False, unique=True, index=True)
    current_stock = Column(Integer, nullable=False, default=0)
    last_stock_in_time = Column(DateTime, nullable=True)
    last_stock_out_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    medicine = relationship("Medicine")
