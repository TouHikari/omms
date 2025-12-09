from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(50), nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    orders = relationship("SupplierOrder", back_populates="supplier")


class SupplierOrder(Base):
    __tablename__ = "supplier_orders"

    id = Column(String(32), primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), nullable=False, default="pending")
    amount = Column(Float, nullable=False, default=0.0)

    supplier = relationship("Supplier", back_populates="orders")
    items = relationship("SupplierOrderItem", back_populates="order", cascade="all, delete-orphan")


class SupplierOrderItem(Base):
    __tablename__ = "supplier_order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(32), ForeignKey("supplier_orders.id"), nullable=False, index=True)
    medicine_id = Column(BigInteger, ForeignKey("medicines.medicine_id"), nullable=False)
    name = Column(String(100), nullable=True)
    qty = Column(Integer, nullable=False, default=1)
    unit = Column(String(20), nullable=True)
    price = Column(Float, nullable=False, default=0.0)

    order = relationship("SupplierOrder", back_populates="items")
