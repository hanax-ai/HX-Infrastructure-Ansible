
#!/usr/bin/env python3
"""
LiteLLM SQLAlchemy Database Initialization Script

This script creates the required database schema for LiteLLM Gateway
using SQLAlchemy with PostgreSQL backend.
"""

import os
import sys
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    create_engine, 
    text, 
    Integer, 
    String, 
    DateTime, 
    JSON, 
    Boolean, 
    ForeignKey, 
    BigInteger,
    MetaData,
    Identity
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import SQLAlchemyError

# Database connection URL from environment variable
DB_URL = os.getenv(
    "LITELLM_DB_URL", 
    "postgresql+psycopg2://litellm_user:REDACTED_PASSWORD@192.168.10.19/litellm_db"
)

# Create engine with connection pooling disabled for initialization
engine = create_engine(
    DB_URL, 
    poolclass=NullPool, 
    future=True, 
    echo=False
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass

class Request(Base):
    """
    Request table to store incoming API requests to LiteLLM Gateway
    
    This table captures all incoming requests with their metadata,
    payload, and initial processing status.
    """
    __tablename__ = "requests"
    
    # Primary key with auto-increment
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamp when request was created
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow
    )
    
    # Unique request identifier for tracking
    request_id: Mapped[str] = mapped_column(
        String(64), 
        nullable=False, 
        unique=True,
        index=True
    )
    
    # API route that was called
    route: Mapped[str] = mapped_column(String(128), nullable=False)
    
    # Model name used for the request
    model: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    
    # JSON payload of the request
    payload: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # HTTP status code of the response
    status_code: Mapped[Optional[int]] = mapped_column(Integer)
    
    # User ID if authentication is enabled
    user_id: Mapped[Optional[str]] = mapped_column(String(128))
    
    # API key used for the request
    api_key: Mapped[Optional[str]] = mapped_column(String(128))
    
    # Request processing start time
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Request processing end time
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)

class Response(Base):
    """
    Response table to store API responses from LiteLLM Gateway
    
    This table captures response data, latency metrics, and links
    back to the original request via foreign key relationship.
    """
    __tablename__ = "responses"
    
    # Primary key with auto-increment
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamp when response was created
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow
    )
    
    # Foreign key to requests table
    request_id_fk: Mapped[int] = mapped_column(
        ForeignKey("requests.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Response latency in milliseconds
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # JSON content of the response
    content: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Token usage information
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Cost information
    cost: Mapped[Optional[float]] = mapped_column(String(32))  # Using String to avoid float precision issues
    
    # Response model (may differ from request model)
    response_model: Mapped[Optional[str]] = mapped_column(String(128))
    
    # Relationship back to request
    request: Mapped[Request] = relationship("Request", backref="responses")

def test_connection() -> bool:
    """
    Test database connectivity
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            if test_value == 1:
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database connection test failed")
                return False
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during connection test: {e}")
        return False

def get_database_info():
    """
    Get database version and connection information
    """
    try:
        with engine.connect() as conn:
            # Get PostgreSQL version
            version_result = conn.execute(text("SELECT version()"))
            version = version_result.scalar()
            print(f"📊 Database version: {version}")
            
            # Get current database name
            db_result = conn.execute(text("SELECT current_database()"))
            db_name = db_result.scalar()
            print(f"📊 Connected to database: {db_name}")
            
            # Get current user
            user_result = conn.execute(text("SELECT current_user"))
            user = user_result.scalar()
            print(f"📊 Connected as user: {user}")
            
    except SQLAlchemyError as e:
        print(f"⚠️  Could not retrieve database info: {e}")

def create_tables() -> bool:
    """
    Create all tables defined in the schema
    
    Returns:
        bool: True if tables created successfully, False otherwise
    """
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        print("✅ Database tables created successfully")
        
        # Verify tables were created
        with engine.connect() as conn:
            # Check if tables exist
            tables_result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('requests', 'responses')
                ORDER BY table_name
            """))
            tables = [row[0] for row in tables_result]
            
            if 'requests' in tables and 'responses' in tables:
                print("✅ Verified tables exist: requests, responses")
                return True
            else:
                print(f"❌ Expected tables not found. Found: {tables}")
                return False
                
    except SQLAlchemyError as e:
        print(f"❌ Failed to create tables: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during table creation: {e}")
        return False

def validate_schema():
    """
    Validate the created schema by checking table structure
    """
    try:
        with engine.connect() as conn:
            # Check requests table structure
            requests_columns = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'requests'
                ORDER BY ordinal_position
            """))
            
            print("\n📋 Requests table structure:")
            for row in requests_columns:
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                print(f"  - {row[0]}: {row[1]} ({nullable})")
            
            # Check responses table structure
            responses_columns = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'responses'
                ORDER BY ordinal_position
            """))
            
            print("\n📋 Responses table structure:")
            for row in responses_columns:
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                print(f"  - {row[0]}: {row[1]} ({nullable})")
                
            # Check foreign key constraints
            fk_result = conn.execute(text("""
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name IN ('requests', 'responses')
            """))
            
            print("\n🔗 Foreign key constraints:")
            for row in fk_result:
                print(f"  - {row[1]}.{row[2]} -> {row[3]}.{row[4]}")
                
    except SQLAlchemyError as e:
        print(f"⚠️  Could not validate schema: {e}")

def bootstrap() -> bool:
    """
    Main bootstrap function to initialize the database
    
    Returns:
        bool: True if bootstrap successful, False otherwise
    """
    print("🚀 Starting LiteLLM Database Initialization")
    print(f"🔗 Database URL: {DB_URL.replace(DB_URL.split('@')[0].split('//')[1], '***:***')}")
    
    # Test connection
    if not test_connection():
        return False
    
    # Get database info
    get_database_info()
    
    # Create tables
    if not create_tables():
        return False
    
    # Validate schema
    validate_schema()
    
    print("\n✅ Database initialization completed successfully!")
    print("\n📝 Next steps:")
    print("  1. Update your LiteLLM config.yaml with the database URL")
    print("  2. Start the LiteLLM Gateway service")
    print("  3. Test API requests to verify logging")
    
    return True

if __name__ == "__main__":
    try:
        success = bootstrap()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Initialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
