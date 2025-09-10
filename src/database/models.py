"""
Database models for Intelligent Trading Bot.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class TradingSession(Base):
    """Trading session model."""
    __tablename__ = "trading_sessions"

    session_id = Column(String(100), primary_key=True, index=True)  # Use session_id as primary key
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="active")  # active, completed, failed
    total_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trades = relationship("Trade", back_populates="session")

class Trade(Base):
    """Individual trade model."""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("trading_sessions.session_id"), nullable=False)
    symbol = Column(String(10), nullable=False)
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    order_type = Column(String(20), default="market")  # market, limit, stop
    status = Column(String(20), default="filled")  # pending, filled, cancelled
    commission = Column(Float, default=0.0)
    pnl = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)

    # Relationships
    session = relationship("TradingSession", back_populates="trades")

class MarketData(Base):
    """Market data storage model."""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    data_source = Column(String(50), default="finnhub")
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentDecision(Base):
    """Agent decision logging model."""
    __tablename__ = "agent_decisions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("trading_sessions.session_id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    decision_type = Column(String(50), nullable=False)  # analysis, trade_signal, risk_assessment
    symbol = Column(String(10), nullable=True)
    confidence = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    decision_metadata = Column(Text, nullable=True)  # JSON string for additional data

class SystemLog(Base):
    """System logging model."""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(10), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    module = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    trace_id = Column(String(50), nullable=True)
    user_id = Column(String(50), nullable=True)