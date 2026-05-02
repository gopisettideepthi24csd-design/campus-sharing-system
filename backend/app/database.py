"""
Database Configuration Module
-----------------------------
This module handles the database connection setup using SQLAlchemy ORM.
It supports both MySQL and SQLite databases via configuration.

For MySQL: Set DATABASE_URL environment variable
For SQLite (default): Uses a local file 'campus_sharing.db'
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL configuration
# Use MySQL if DATABASE_URL is set, otherwise fallback to SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./campus_sharing.db"  # SQLite fallback for easy setup
)

# For MySQL, the URL format would be:
# "mysql+pymysql://username:password@localhost:3306/campus_sharing"

# Create the SQLAlchemy engine
# connect_args is needed only for SQLite to allow multi-threaded access
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # Required for SQLite
    )
else:
    engine = create_engine(DATABASE_URL)

# SessionLocal class - each instance will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    Dependency function to get a database session.
    Used with FastAPI's Depends() for dependency injection.
    Ensures the session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
