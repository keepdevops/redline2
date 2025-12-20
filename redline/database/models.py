"""
SQLAlchemy Database Models for VarioSync
Simplified schema - file storage handled by Wasabi S3 (not PostgreSQL)
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """Main user table (stores user data linked to Supabase auth.users)"""
    __tablename__ = 'users'

    # user_id matches auth.users.id but no FK constraint (auth schema managed by Supabase)
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String, nullable=False, unique=True)
    name = Column(String)
    company = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hours = relationship("UserHours", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("UsageSession", back_populates="user", cascade="all, delete-orphan")
    usage_history = relationship("UsageHistory", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("PaymentHistory", back_populates="user", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"


class UserHours(Base):
    """User hours balance and usage tracking (auxiliary table)"""
    __tablename__ = 'user_hours'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False, unique=True)
    hours_remaining = Column(Float, default=0.0)
    total_hours_purchased = Column(Float, default=0.0)
    total_hours_used = Column(Float, default=0.0)
    last_deduction_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="hours")

    # Indexes
    __table_args__ = (
        Index('idx_user_hours_user', 'user_id'),
    )

    def __repr__(self):
        return f"<UserHours(user_id={self.user_id}, hours_remaining={self.hours_remaining})>"


class UsageSession(Base):
    """Active user sessions"""
    __tablename__ = 'usage_sessions'

    session_id = Column(String, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    total_hours = Column(Float)
    total_seconds = Column(Float)
    status = Column(String, default='active')
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")

    # Indexes
    __table_args__ = (
        Index('idx_usage_sessions_user', 'user_id'),
        Index('idx_usage_sessions_start', 'start_time'),
    )

    def __repr__(self):
        return f"<UsageSession(session_id={self.session_id}, user_id={self.user_id})>"


class UsageHistory(Base):
    """Hour deduction audit log"""
    __tablename__ = 'usage_history'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    session_id = Column(String)
    hours_deducted = Column(Float, nullable=False)
    deduction_time = Column(DateTime, nullable=False)
    hours_remaining_before = Column(Float)
    hours_remaining_after = Column(Float)
    api_endpoint = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="usage_history")

    # Indexes
    __table_args__ = (
        Index('idx_usage_history_user', 'user_id'),
        Index('idx_usage_history_time', 'deduction_time'),
    )

    def __repr__(self):
        return f"<UsageHistory(id={self.id}, hours_deducted={self.hours_deducted})>"


class PaymentHistory(Base):
    """Stripe payment transactions"""
    __tablename__ = 'payment_history'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    stripe_session_id = Column(String)
    payment_id = Column(String)
    hours_purchased = Column(Float, nullable=False)
    amount_paid = Column(Float, nullable=False)
    currency = Column(String, default='usd')
    payment_status = Column(String)
    payment_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payments")

    # Indexes
    __table_args__ = (
        Index('idx_payment_history_user', 'user_id'),
        Index('idx_payment_history_date', 'payment_date'),
    )

    def __repr__(self):
        return f"<PaymentHistory(id={self.id}, hours_purchased={self.hours_purchased})>"


class AccessLog(Base):
    """API endpoint access logs"""
    __tablename__ = 'access_logs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=False)
    session_id = Column(String)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    ip_address = Column(String)
    user_agent = Column(String)
    response_status = Column(Integer)
    response_time_ms = Column(Integer)
    access_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="access_logs")

    # Indexes
    __table_args__ = (
        Index('idx_access_logs_user', 'user_id'),
        Index('idx_access_logs_time', 'access_time'),
        Index('idx_access_logs_endpoint', 'endpoint'),
    )

    def __repr__(self):
        return f"<AccessLog(id={self.id}, endpoint={self.endpoint})>"
