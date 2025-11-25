from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship

from .session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)   # FIXED (not unique)

    images = relationship("Image", back_populates="user", cascade="all, delete")
    storage_used = Column(Integer, default=0)
    is_admin = Column(Integer, default=0)  # 1 = admin, 0 = regular

class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True)

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    user = relationship("User", back_populates="images")

    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)

    embedding = Column(Vector(dim=512), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), index=True)
    expires_at = Column(DateTime, nullable=True)

class AppConfig(Base):
    __tablename__ = "app_config"

    id = Column(Integer, primary_key=True)
    max_users = Column(Integer, default=50)
    per_user_storage_limit = Column(Integer, default=1_000_000_000)  # 1 GB
