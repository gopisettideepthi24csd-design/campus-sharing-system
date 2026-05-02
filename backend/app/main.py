"""
Main Application Module
-----------------------
Entry point for the Campus Sharing and Resource Sharing System.

This module:
1. Creates the FastAPI application instance
2. Configures CORS middleware (for frontend-backend communication)
3. Registers all API routers
4. Creates database tables on startup
5. Seeds sample data (books) on first run
6. Serves the frontend static files
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .database import engine, Base, SessionLocal
from .models.models import User, Resource, Book, Request
from .routers import auth_router, resources_router, books_router, requests_router
from .utils.auth import hash_password

# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="Campus Sharing and Resource Sharing System",
    description="A platform for students to share resources, books, and manage borrowing.",
    version="1.0.0"
)

# ============================================================
# CORS MIDDLEWARE
# ============================================================
# Allows the frontend (running on a different port) to communicate with the backend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ============================================================
# REGISTER ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(resources_router)
app.include_router(books_router)
app.include_router(requests_router)


# ============================================================
# DATABASE INITIALIZATION & SEED DATA
# ============================================================

@app.on_event("startup")
def startup_event():
    """
    Runs when the application starts.
    - Creates all database tables
    - Seeds sample data if database is empty
    """
    # Create all tables defined in models
    Base.metadata.create_all(bind=engine)
    
    # Seed sample data
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@campus.edu").first()
        if not admin:
            # Create admin user
            admin = User(
                name="Admin",
                email="admin@campus.edu",
                password=hash_password("admin123"),
                role="admin"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            
            # Create sample student user
            student = User(
                name="John Student",
                email="john@campus.edu",
                password=hash_password("student123"),
                role="student"
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            
            # Seed sample books (as specified in requirements)
            sample_books = [
                Book(
                    title="Data Structures",
                    author="Ellis Horowitz",
                    subject="Computer Science",
                    status="Available",
                    owner_id=admin.id
                ),
                Book(
                    title="Operating System Concepts",
                    author="Abraham Silberschatz",
                    subject="Computer Science",
                    status="Available",
                    owner_id=admin.id
                ),
                Book(
                    title="Computer Networks",
                    author="Andrew S. Tanenbaum",
                    subject="Computer Science",
                    status="Available",
                    owner_id=admin.id
                ),
                Book(
                    title="Database System Concepts",
                    author="Abraham Silberschatz",
                    subject="Computer Science",
                    status="Available",
                    owner_id=admin.id
                ),
            ]
            
            for book in sample_books:
                db.add(book)
            
            # Seed sample resources
            sample_resources = [
                Resource(
                    title="Python Programming Notes",
                    description="Complete notes covering Python basics to advanced topics",
                    category="Notes",
                    status="Available",
                    owner_id=admin.id
                ),
                Resource(
                    title="Arduino Starter Kit",
                    description="Arduino UNO with sensors and components for IoT projects",
                    category="Electronics",
                    status="Available",
                    owner_id=admin.id
                ),
                Resource(
                    title="Web Development Toolkit",
                    description="Collection of tools and templates for web development",
                    category="Tools",
                    status="Available",
                    owner_id=student.id
                ),
            ]
            
            for resource in sample_resources:
                db.add(resource)
            
            db.commit()
            print("✓ Database seeded with sample data")
        
    finally:
        db.close()


# ============================================================
# SERVE FRONTEND STATIC FILES
# ============================================================

# Get the path to frontend directory
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")

# Mount static files (CSS, JS)
if os.path.exists(frontend_dir):
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")


# ============================================================
# SERVE FRONTEND HTML PAGES
# ============================================================

@app.get("/")
def serve_index():
    """Serve the main login/register page"""
    return FileResponse(os.path.join(frontend_dir, "index.html"))


@app.get("/dashboard")
def serve_dashboard():
    """Serve the dashboard page"""
    return FileResponse(os.path.join(frontend_dir, "dashboard.html"))


@app.get("/books-page")
def serve_books():
    """Serve the books page"""
    return FileResponse(os.path.join(frontend_dir, "books.html"))


@app.get("/resources-page")
def serve_resources():
    """Serve the resources page"""
    return FileResponse(os.path.join(frontend_dir, "resources.html"))


@app.get("/my-requests")
def serve_my_requests():
    """Serve the my requests page"""
    return FileResponse(os.path.join(frontend_dir, "my-requests.html"))


@app.get("/received-requests")
def serve_received_requests():
    """Serve the received requests page"""
    return FileResponse(os.path.join(frontend_dir, "received-requests.html"))


# ============================================================
# HEALTH CHECK ENDPOINT
# ============================================================

@app.get("/api/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "message": "Campus Sharing System API is running"}
