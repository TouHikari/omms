from sqlalchemy.orm import declarative_base


Base = declarative_base()

# 导出所有模型类
from .user import User
from .patient import Patient
from .appointment import Appointment
from .record import MedicalRecord as Record
