from typing import Optional

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    real_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[int] = mapped_column(Integer, default=1, index=True)
    created_at: Mapped[Optional[str]] = mapped_column(String(19), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(19), nullable=True)
    last_login_at: Mapped[Optional[str]] = mapped_column(String(19), nullable=True)
    role_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, index=True)
