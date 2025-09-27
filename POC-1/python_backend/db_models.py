
"""
SQLAlchemy Database Models for LiteLLM Integration
==================================================

This module defines the SQLAlchemy models that replace Prisma
in the LiteLLM Gateway implementation.

Models:
- Request: Logs all incoming API requests
- Response: Logs all API responses with performance metrics

Key Features:
- Foreign key relationships (Response.request_id_fk -> Request.id)
- Optimized indexes for performance
- Connection pooling for production use
- SCRAM-SHA-256 authentication support
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://litellm_user@db-b8d99fca9.db002.hosteddb.reai.io:5432/b8d99fca9?connect_timeout=15"
)

# Create SQLAlchemy engine with production-ready configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Connection pool size
    max_overflow=20,       # Additional connections if pool is full
    pool_pre_ping=True,    # Validate connections before use
    pool_recycle=3600,     # Recycle connections every hour
    echo=False             # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

class Request(Base):
    """
    Request model - logs all incoming API requests
    
    This table captures all request metadata needed for
    monitoring, debugging, and billing purposes.
    """
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(255), unique=True, index=True, nullable=False)
    route = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    url = Column(Text, nullable=False)
    headers = Column(Text)  # JSON string
    body = Column(Text)     # JSON string
    model = Column(String(100), nullable=False, index=True)
    status_code = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationship to responses
    responses = relationship("Response", back_populates="request", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Request(id={self.id}, request_id='{self.request_id}', model='{self.model}')>"

class Response(Base):
    """
    Response model - logs all API responses with performance metrics
    
    This table captures response data, performance metrics,
    and billing information with foreign key to requests.
    """
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id_fk = Column(Integer, ForeignKey("requests.id"), nullable=False, index=True)
    response_body = Column(Text, nullable=False)  # JSON string
    status_code = Column(Integer, nullable=False, index=True)
    latency_ms = Column(Numeric(10, 2), nullable=False, index=True)
    tokens_used = Column(Integer, nullable=False)
    cost = Column(Numeric(10, 6), nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationship to request
    request = relationship("Request", back_populates="responses")
    
    def __repr__(self):
        return f"<Response(id={self.id}, request_id_fk={self.request_id_fk}, latency_ms={self.latency_ms})>"

def get_database_url():
    """Get database URL with environment variable override"""
    return DATABASE_URL

def create_tables():
    """Create all tables in the database"""
    try:
        logger.info(f"Database engine created for: {DATABASE_URL.split('@')[1].split('?')[0]}")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1 as test").fetchone()
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def get_db() -> Session:
    """
    Dependency function to get database session
    
    Usage in FastAPI endpoints:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables and test connection"""
    logger.info("Initializing database...")
    
    if not create_tables():
        logger.error("Failed to create database tables")
        return False
    
    if not test_connection():
        logger.error("Database connection test failed")
        return False
    
    logger.info("✅ SQLAlchemy database initialized successfully")
    return True

if __name__ == "__main__":
    # Direct execution for testing
    init_database()
