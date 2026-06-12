from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    imei = Column(String(15), unique=True, index=True)
    storage = Column(String(20))
    color = Column(String(30))
    purchase_date = Column(Date)
    battery_health = Column(Integer)
    appearance = Column(String(20))
    repair_history = Column(Text)
    notes = Column(Text)
    estimated_price = Column(Float)
    status = Column(String(20), default="在库待售", index=True)
    is_deleted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    created_by = Column(String(50))
    updated_by = Column(String(50))
    deleted_by = Column(String(50))

    inspections = relationship("Inspection", back_populates="device", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="device", cascade="all, delete-orphan")


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    inspection_date = Column(Date, nullable=False, index=True)
    appearance_grade = Column(String(10), nullable=False)
    function_items = Column(Text, nullable=False)
    battery_health = Column(Integer)
    estimated_value = Column(Float)
    appraiser_signature = Column(String(100), nullable=False)
    notes = Column(Text)
    is_deleted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    created_by = Column(String(50))
    updated_by = Column(String(50))
    deleted_by = Column(String(50))

    device = relationship("Device", back_populates="inspections")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    trade_type = Column(String(20), nullable=False, index=True)
    actual_amount = Column(Float, nullable=False)
    counterparty_name = Column(String(100), nullable=False)
    trade_date = Column(Date, nullable=False, index=True)
    settlement_method = Column(String(20), nullable=False)
    notes = Column(Text)
    is_deleted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    created_by = Column(String(50))
    updated_by = Column(String(50))
    deleted_by = Column(String(50))

    device = relationship("Device", back_populates="transactions")
