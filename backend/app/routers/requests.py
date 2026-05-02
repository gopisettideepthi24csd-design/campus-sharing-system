"""
Requests Router
---------------
Handles the borrow request and approval workflow.

Workflow:
1. User sends request → status = Pending
2. Owner/Admin approves → status = Approved, item = Borrowed
3. Owner/Admin rejects → status = Rejected
4. User returns item → status = Returned, item = Available

Endpoints:
- POST /api/requests              - Create a new borrow request
- GET  /api/requests/my           - Get requests made by current user
- GET  /api/requests/received     - Get requests received (for approval)
- PUT  /api/requests/{id}/action  - Approve or reject a request
- PUT  /api/requests/{id}/return  - Mark item as returned
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models.models import User, Resource, Book, Request
from ..schemas.schemas import RequestCreate, RequestAction, RequestResponse
from ..utils.auth import get_current_user

# Create router
router = APIRouter(prefix="/api/requests", tags=["Requests"])


# ============================================================
# HELPER: Build request response with names
# ============================================================

def build_request_response(req: Request, db: Session) -> RequestResponse:
    """Helper to build a complete request response with user and item names."""
    requester = db.query(User).filter(User.id == req.requester_id).first()
    owner = db.query(User).filter(User.id == req.owner_id).first()
    
    # Get item title based on type
    item_title = ""
    if req.item_type == "resource":
        item = db.query(Resource).filter(Resource.id == req.item_id).first()
        item_title = item.title if item else "Unknown"
    elif req.item_type == "book":
        item = db.query(Book).filter(Book.id == req.item_id).first()
        item_title = item.title if item else "Unknown"
    
    return RequestResponse(
        id=req.id,
        item_id=req.item_id,
        item_type=req.item_type,
        requester_id=req.requester_id,
        owner_id=req.owner_id,
        status=req.status,
        borrow_date=req.borrow_date,
        return_date=req.return_date,
        created_at=req.created_at,
        requester_name=requester.name if requester else "Unknown",
        owner_name=owner.name if owner else "Unknown",
        item_title=item_title
    )


# ============================================================
# CREATE BORROW REQUEST
# ============================================================

@router.post("/", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    request_data: RequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new borrow request.
    
    Validations:
    - Item must exist
    - Item must be Available
    - User cannot request their own item
    - No duplicate pending requests
    """
    # Determine the item and its owner
    if request_data.item_type == "resource":
        item = db.query(Resource).filter(Resource.id == request_data.item_id).first()
    elif request_data.item_type == "book":
        item = db.query(Book).filter(Book.id == request_data.item_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid item_type. Use 'resource' or 'book'")
    
    # Check if item exists
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if item is available
    if item.status != "Available":
        raise HTTPException(status_code=400, detail="Item is not available for borrowing")
    
    # User cannot request their own item
    if item.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot request your own item")
    
    # Check for existing pending request
    existing = db.query(Request).filter(
        Request.item_id == request_data.item_id,
        Request.item_type == request_data.item_type,
        Request.requester_id == current_user.id,
        Request.status == "Pending"
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="You already have a pending request for this item")
    
    # Create the request
    new_request = Request(
        item_id=request_data.item_id,
        item_type=request_data.item_type,
        requester_id=current_user.id,
        owner_id=item.owner_id,
        status="Pending"
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return build_request_response(new_request, db)


# ============================================================
# GET MY REQUESTS (requests I've made)
# ============================================================

@router.get("/my", response_model=List[RequestResponse])
def get_my_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all requests made by the current user."""
    requests = db.query(Request).filter(
        Request.requester_id == current_user.id
    ).order_by(Request.created_at.desc()).all()
    
    return [build_request_response(r, db) for r in requests]


# ============================================================
# GET RECEIVED REQUESTS (requests for my items)
# ============================================================

@router.get("/received", response_model=List[RequestResponse])
def get_received_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all requests received for the current user's items.
    Admin can see all requests.
    """
    if current_user.role == "admin":
        # Admin sees all requests
        requests = db.query(Request).order_by(Request.created_at.desc()).all()
    else:
        # Regular user sees only requests for their items
        requests = db.query(Request).filter(
            Request.owner_id == current_user.id
        ).order_by(Request.created_at.desc()).all()
    
    return [build_request_response(r, db) for r in requests]


# ============================================================
# APPROVE OR REJECT REQUEST
# ============================================================

@router.put("/{request_id}/action", response_model=RequestResponse)
def handle_request_action(
    request_id: int,
    action_data: RequestAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve or reject a borrow request.
    
    Only the item owner or admin can perform this action.
    
    When approved:
    - Request status → Approved
    - Item status → Borrowed
    - Borrow date is recorded
    
    When rejected:
    - Request status → Rejected
    """
    # Find the request
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check authorization (owner or admin)
    if req.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to handle this request")
    
    # Request must be in Pending status
    if req.status != "Pending":
        raise HTTPException(status_code=400, detail="Request is not in Pending status")
    
    # Process the action
    if action_data.action == "approve":
        # Update request status
        req.status = "Approved"
        req.borrow_date = datetime.utcnow()
        
        # Update item status to Borrowed
        if req.item_type == "resource":
            item = db.query(Resource).filter(Resource.id == req.item_id).first()
        else:
            item = db.query(Book).filter(Book.id == req.item_id).first()
        
        if item:
            item.status = "Borrowed"
        
    elif action_data.action == "reject":
        req.status = "Rejected"
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'")
    
    db.commit()
    db.refresh(req)
    
    return build_request_response(req, db)


# ============================================================
# RETURN ITEM
# ============================================================

@router.put("/{request_id}/return", response_model=RequestResponse)
def return_item(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an item as returned.
    
    Can be done by the requester, owner, or admin.
    
    When returned:
    - Request status → Returned
    - Item status → Available
    - Return date is recorded
    """
    # Find the request
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Check authorization
    if (req.requester_id != current_user.id and 
        req.owner_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Request must be in Approved status to return
    if req.status != "Approved":
        raise HTTPException(status_code=400, detail="Item can only be returned if request is Approved")
    
    # Update request status
    req.status = "Returned"
    req.return_date = datetime.utcnow()
    
    # Update item status back to Available
    if req.item_type == "resource":
        item = db.query(Resource).filter(Resource.id == req.item_id).first()
    else:
        item = db.query(Book).filter(Book.id == req.item_id).first()
    
    if item:
        item.status = "Available"
    
    db.commit()
    db.refresh(req)
    
    return build_request_response(req, db)
