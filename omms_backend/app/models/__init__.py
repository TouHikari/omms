from sqlalchemy.orm import declarative_base


Base = declarative_base()

# 导出所有模型类
from .user import User
from .patient import Patient
from .appointment import Appointment
from .record import MedicalRecord as Record
from .medicine import Medicine
from .inventory import InventoryBatch, InventoryLog, MedicineStock
from .prescription import Prescription, PrescriptionItem
from .supplier import Supplier, SupplierOrder, SupplierOrderItem
