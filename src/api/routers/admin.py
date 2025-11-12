from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional  # Ensure List is imported
from uuid import UUID
from ... import services, security, database
from ...schemas import user as user_schema
from ...models import Customer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/users",
    response_model=user_schema.UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create user with specific role (Admin only)"
)
def create_user_by_admin(
    user: user_schema.AdminUserCreate,
    db: Session = Depends(database.get_db),
    current_user: Customer = Depends(security.get_admin_user)
):
    """Admin creates a user with a specified role."""
    db_user = services.user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return services.user_service.create_user_with_role(db=db, user=user)


@router.get(
    "/users",
    response_model=user_schema.UserListResponse,
    summary="Get all users (Admin only)"
)
def list_users(
    role: Optional[str] = Query(None, description="Filter by role: customer, delivery_guy, admin"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(database.get_db),
    current_user: Customer = Depends(security.get_admin_user)
):
    """Get a list of all users, with optional role filtering."""
    if role:
        users = services.user_service.get_users_by_role(db, role=role, skip=skip, limit=limit)
    else:
        users = services.user_service.get_all_users(db, skip=skip, limit=limit)
    return {"users": users, "total": len(users)}


@router.get(
    "/users/{user_id}",
    response_model=user_schema.UserPublic,
    summary="Get user by ID (Admin only)"
)
def get_user(
    user_id: UUID,
    db: Session = Depends(database.get_db),
    current_user: Customer = Depends(security.get_admin_user)
):
    """Get a specific user by their ID."""
    user = services.user_service.get_user_by_id(db, customer_id=str(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch(
    "/users/{user_id}",
    response_model=user_schema.UserPublic,
    summary="Update user (Admin only)"
)
def update_user(
    user_id: UUID,
    user_update: user_schema.UserUpdate,
    db: Session = Depends(database.get_db),
    current_user: Customer = Depends(security.get_admin_user)
):
    """Update a user's information."""
    user = services.user_service.update_user(db, customer_id=user_id, user_update=user_update)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Deactivate user (Admin only)"
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(database.get_db),
    current_user: Customer = Depends(security.get_admin_user)
):
    """Deactivate a user (soft delete)."""
    if str(user_id) == str(current_user.customer_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate your own account")
    success = services.user_service.delete_user(db, customer_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deactivated successfully", "user_id": str(user_id)}


# --- THIS IS THE NEW ENDPOINT FOR THE VEHICLE PAGE ---
@router.get(
    "/delivery-personnel",
    response_model=List[user_schema.UserPublic],
    summary="Get all delivery personnel (Admin only)",
    description="Lists all users with the 'delivery_guy' role to populate driver selection forms."
)
def list_delivery_personnel(
    db: Session = Depends(database.get_db),
    current_user: Customer = Depends(security.get_admin_user)
):
    """Get a list of all users who can be assigned as drivers."""
    try:
        # This reuses your existing user service to find users by their role
        return services.user_service.get_users_by_role(db, role="delivery_guy")
    except Exception as e:
        logger.error(f"Unexpected error listing delivery personnel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching delivery personnel"
        )