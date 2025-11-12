from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import UUID
from ..models import Customer
from ..schemas import user as user_schema
from ..hashing import get_password_hash


def get_user_by_email(db: Session, email: str) -> Customer:
    """Get user by email address"""
    return db.query(Customer).filter(Customer.email == email).first()


def get_user_by_id(db: Session, customer_id: str) -> Customer:
    """Get user by customer ID"""
    return (
        db.query(Customer)
        .filter(Customer.customer_id == UUID(customer_id))
        .first()
    )


def create_user(db: Session, user: user_schema.UserCreate, role: str = "customer") -> Customer:
    """Create a new user with specified role"""
    hashed_password = get_password_hash(user.password)
    db_user = Customer(
        email=user.email,
        name=user.name,
        phone=getattr(user, 'phone', None),
        hashed_password=hashed_password,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_with_role(db: Session, user: user_schema.AdminUserCreate) -> Customer:
    """Create a new user with admin-specified role"""
    hashed_password = get_password_hash(user.password)
    db_user = Customer(
        email=user.email,
        name=user.name,
        phone=user.phone,
        hashed_password=hashed_password,
        role=user.role.value
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[Customer]:
    """Get all users (admin only)"""
    return db.query(Customer).offset(skip).limit(limit).all()


def get_users_by_role(db: Session, role: str, skip: int = 0, limit: int = 1000) -> list[Customer]:
    """
    Get users by role.
    The default limit has been increased from 100 to 1000 to ensure all delivery personnel
    are fetched for the driver assignment dropdown.
    """
    return db.query(Customer).filter(Customer.role == role).offset(skip).limit(limit).all()


def update_user(db: Session, customer_id: UUID, user_update: user_schema.UserUpdate) -> Customer:
    """Update user information"""
    db_user = get_user_by_id(db, str(customer_id))
    if not db_user:
        return None
    
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.phone is not None:
        db_user.phone = user_update.phone
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, customer_id: UUID) -> bool:
    """Delete a user (soft delete by setting is_active=False)"""
    db_user = get_user_by_id(db, str(customer_id))
    if not db_user:
        return False
    
    db_user.is_active = False
    db.commit()
    return True


def update_user_last_login(db: Session, customer_id: UUID) -> Customer:
    """Update user's last login timestamp"""
    db_user = get_user_by_id(db, str(customer_id))
    if db_user:
        db_user.last_login = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_user)
    return db_user
