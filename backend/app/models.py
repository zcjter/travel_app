from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Date, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    cover_image = Column(String(256), default="")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    description = Column(Text, default="")
    status = Column(String(32), default="planning")  # planning / ongoing / completed
    budget = Column(Float, nullable=True)
    destination = Column(String(128), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    moments = relationship("Moment", back_populates="trip", cascade="all, delete-orphan",
                           order_by="Moment.created_at")


class Moment(Base):
    __tablename__ = "moments"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, default="")
    location_name = Column(String(128), default="")
    weather_info = Column(Text, default="")  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trip = relationship("Trip", back_populates="moments")
    media_list = relationship("Media", back_populates="moment", cascade="all, delete-orphan")


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    moment_id = Column(Integer, ForeignKey("moments.id", ondelete="CASCADE"), nullable=True)
    file_path = Column(String(256), nullable=False)
    file_type = Column(String(16), default="image")  # image / video
    thumbnail_path = Column(String(256), default="")
    exif = Column(Text, default="")  # JSON string
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    moment = relationship("Moment", back_populates="media_list")
