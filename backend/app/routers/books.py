"""
Books Router
------------
Handles CRUD operations for books.

Endpoints:
- GET    /api/books         - Get all books (with search/filter)
- GET    /api/books/my      - Get current user's books
- POST   /api/books         - Add a new book
- DELETE /api/books/{id}    - Delete a book (owner only)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.models import User, Book
from ..schemas.schemas import BookCreate, BookResponse
from ..utils.auth import get_current_user

# Create router
router = APIRouter(prefix="/api/books", tags=["Books"])


# ============================================================
# GET ALL BOOKS
# ============================================================

@router.get("/", response_model=List[BookResponse])
def get_all_books(
    search: Optional[str] = Query(None, description="Search by title or author"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get all books with optional search and filter.
    
    Query Parameters:
    - search: Search in title or author (partial match)
    - subject: Filter by subject
    - status: Filter by status (Available/Borrowed)
    """
    query = db.query(Book)
    
    # Apply search filter
    if search:
        query = query.filter(
            (Book.title.ilike(f"%{search}%")) | 
            (Book.author.ilike(f"%{search}%"))
        )
    
    # Apply subject filter
    if subject:
        query = query.filter(Book.subject == subject)
    
    # Apply status filter
    if status_filter:
        query = query.filter(Book.status == status_filter)
    
    books = query.order_by(Book.created_at.desc()).all()
    
    # Build response with owner names
    result = []
    for b in books:
        owner = db.query(User).filter(User.id == b.owner_id).first()
        result.append(BookResponse(
            id=b.id,
            title=b.title,
            author=b.author,
            subject=b.subject,
            status=b.status,
            owner_id=b.owner_id,
            owner_name=owner.name if owner else "Unknown",
            created_at=b.created_at
        ))
    
    return result


# ============================================================
# GET MY BOOKS
# ============================================================

@router.get("/my", response_model=List[BookResponse])
def get_my_books(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all books owned by the current user."""
    books = db.query(Book).filter(
        Book.owner_id == current_user.id
    ).order_by(Book.created_at.desc()).all()
    
    result = []
    for b in books:
        result.append(BookResponse(
            id=b.id,
            title=b.title,
            author=b.author,
            subject=b.subject,
            status=b.status,
            owner_id=b.owner_id,
            owner_name=current_user.name,
            created_at=b.created_at
        ))
    
    return result


# ============================================================
# ADD NEW BOOK
# ============================================================

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def add_book(
    book_data: BookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new book to the system.
    The current user becomes the owner.
    """
    new_book = Book(
        title=book_data.title,
        author=book_data.author,
        subject=book_data.subject,
        status="Available",
        owner_id=current_user.id
    )
    
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return BookResponse(
        id=new_book.id,
        title=new_book.title,
        author=new_book.author,
        subject=new_book.subject,
        status=new_book.status,
        owner_id=new_book.owner_id,
        owner_name=current_user.name,
        created_at=new_book.created_at
    )


# ============================================================
# DELETE BOOK
# ============================================================

@router.delete("/{book_id}", status_code=status.HTTP_200_OK)
def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a book. Only the owner or admin can delete."""
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this book")
    
    db.delete(book)
    db.commit()
    
    return {"message": "Book deleted successfully"}
