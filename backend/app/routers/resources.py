"""
Resources Router
----------------
Handles CRUD operations for shared resources (notes, tools, etc.)

Endpoints:
- GET    /api/resources         - Get all resources (with search/filter)
- GET    /api/resources/my      - Get current user's resources
- POST   /api/resources         - Add a new resource
- DELETE /api/resources/{id}    - Delete a resource (owner only)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models.models import User, Resource
from ..schemas.schemas import ResourceCreate, ResourceResponse
from ..utils.auth import get_current_user

# Create router
router = APIRouter(prefix="/api/resources", tags=["Resources"])


# ============================================================
# GET ALL RESOURCES
# ============================================================

@router.get("/", response_model=List[ResourceResponse])
def get_all_resources(
    search: Optional[str] = Query(None, description="Search by title"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get all resources with optional search and filter.
    
    Query Parameters:
    - search: Search in title (partial match)
    - category: Filter by exact category
    - status: Filter by status (Available/Borrowed)
    """
    # Start with base query
    query = db.query(Resource)
    
    # Apply search filter (case-insensitive partial match)
    if search:
        query = query.filter(Resource.title.ilike(f"%{search}%"))
    
    # Apply category filter
    if category:
        query = query.filter(Resource.category == category)
    
    # Apply status filter
    if status_filter:
        query = query.filter(Resource.status == status_filter)
    
    # Execute query and get results
    resources = query.order_by(Resource.created_at.desc()).all()
    
    # Build response with owner names
    result = []
    for r in resources:
        owner = db.query(User).filter(User.id == r.owner_id).first()
        result.append(ResourceResponse(
            id=r.id,
            title=r.title,
            description=r.description,
            category=r.category,
            status=r.status,
            owner_id=r.owner_id,
            owner_name=owner.name if owner else "Unknown",
            created_at=r.created_at
        ))
    
    return result


# ============================================================
# GET MY RESOURCES
# ============================================================

@router.get("/my", response_model=List[ResourceResponse])
def get_my_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all resources owned by the current user.
    Requires authentication.
    """
    resources = db.query(Resource).filter(
        Resource.owner_id == current_user.id
    ).order_by(Resource.created_at.desc()).all()
    
    result = []
    for r in resources:
        result.append(ResourceResponse(
            id=r.id,
            title=r.title,
            description=r.description,
            category=r.category,
            status=r.status,
            owner_id=r.owner_id,
            owner_name=current_user.name,
            created_at=r.created_at
        ))
    
    return result


# ============================================================
# ADD NEW RESOURCE
# ============================================================

@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def add_resource(
    resource_data: ResourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new resource to the system.
    The current user becomes the owner.
    """
    # Create new resource
    new_resource = Resource(
        title=resource_data.title,
        description=resource_data.description,
        category=resource_data.category,
        status="Available",  # New resources are always available
        owner_id=current_user.id
    )
    
    # Save to database
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    
    return ResourceResponse(
        id=new_resource.id,
        title=new_resource.title,
        description=new_resource.description,
        category=new_resource.category,
        status=new_resource.status,
        owner_id=new_resource.owner_id,
        owner_name=current_user.name,
        created_at=new_resource.created_at
    )


# ============================================================
# DELETE RESOURCE
# ============================================================

@router.delete("/{resource_id}", status_code=status.HTTP_200_OK)
def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a resource. Only the owner or admin can delete.
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Check ownership or admin role
    if resource.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this resource")
    
    db.delete(resource)
    db.commit()
    
    return {"message": "Resource deleted successfully"}
