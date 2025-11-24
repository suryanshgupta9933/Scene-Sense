from sqlalchemy import Column, String, DateTime, ForeignKey
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
