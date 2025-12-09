from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, DECIMAL
from datetime import datetime
from app.models import Base


class Medicine(Base):
    __tablename__ = "medicines"

    medicine_id = Column(BigInteger, primary_key=True, autoincrement=True)
    medicine_name = Column(String(100), nullable=False)
    specification = Column(String(100), nullable=False)
    dosage_form = Column(String(50), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    unit = Column(String(20), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    warning_stock = Column(Integer, nullable=False, default=50)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
