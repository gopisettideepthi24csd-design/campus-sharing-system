"""
Database Models Module
----------------------
Defines all database tables using SQLAlchemy ORM.
Tables: users, resources, books, requests

Each model maps to a database table and defines:
- Column types and constraints
- Relationships between tables
- Default values
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


# ============================================================
# ENUM DEFINITIONS
# ============================================================

class UserRole(str, enum.Enum):
    """User roles in the system"""
    student = "student"
    admin = "admin"


class ItemStatus(str, enum.Enum):
    """Status of a resource or book"""
    Available = "Available"
    Borrowed = "Borrowed"


class RequestStatus(str, enum.Enum):
    """Status of a borrow request"""
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"
    Returned = "Returned"


# ============================================================
# USER MODEL
# ============================================================

class User(Base):
    """
    Users table - stores all registered users.
    Fields: id, name, email, password (hashed), role, created_at
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Stores hashed password
    role = Column(String(20), default="student")  # 'student' or 'admin'
    created_at = Column(DateTime, server_default=func.now())

    # Relationships - a user can own resources and books
    resources = relationship("Resource", back_populates="owner")
    books = relationship("Book", back_populates="owner")


# ============================================================
# RESOURCE MODEL
# ============================================================

class Resource(Base):
    """
    Resources table - stores shared items (notes, tools, etc.)
    Fields: id, title, description, category, status, owner_id, created_at
    """
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # e.g., Notes, Tools, Electronics
    status = Column(String(20), default="Available")  # Available or Borrowed
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship back to user
    owner = relationship("User", back_populates="resources")


# ============================================================
# BOOK MODEL
# ============================================================

class Book(Base):
    """
    Books table - stores books available for sharing.
    Fields: id, title, author, subject, status, owner_id, created_at
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=True)
    subject = Column(String(100), nullable=True)
    status = Column(String(20), default="Available")  # Available or Borrowed
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship back to user
    owner = relationship("User", back_populates="books")


# ============================================================
# REQUEST MODEL
# ============================================================

class Request(Base):
    """
    Requests table - stores borrow requests.
    Tracks the full lifecycle: Pending → Approved/Rejected → Returned
    
    Fields: id, item_id, item_type, requester_id, owner_id, 
            status, borrow_date, return_date, created_at
    """
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_id = Column(Integer, nullable=False)  # ID of the resource or book
    item_type = Column(String(20), nullable=False)  # 'resource' or 'book'
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="Pending")  # Pending/Approved/Rejected/Returned
    borrow_date = Column(DateTime, nullable=True)  # Set when approved
    return_date = Column(DateTime, nullable=True)  # Set when returned
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id])
    owner = relationship("User", foreign_keys=[owner_id])
