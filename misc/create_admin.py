"""
Script to create the first admin user
Run this once to set up the initial admin account
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database import SessionLocal
from src.models import Customer
from src.hashing import get_password_hash
from uuid import uuid4
from datetime import datetime

def create_admin():
    """Create the first admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(Customer).filter(Customer.role == "admin").first()
        if existing_admin:
            print(f"⚠️  Admin user already exists: {existing_admin.email}")
            response = input("Do you want to create another admin? (y/n): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        
        # Get admin details
        print("\n" + "="*50)
        print("CREATE ADMIN USER")
        print("="*50 + "\n")
        
        email = input("Enter admin email: ").strip()
        if not email:
            print("❌ Email is required")
            return
        
        # Check if email already exists
        existing_user = db.query(Customer).filter(Customer.email == email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists")
            return
        
        name = input("Enter admin name: ").strip()
        if not name:
            print("❌ Name is required")
            return
        
        phone = input("Enter admin phone (optional): ").strip() or None
        
        password = input("Enter admin password (min 8 characters): ").strip()
        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            return
        
        password_confirm = input("Confirm password: ").strip()
        if password != password_confirm:
            print("❌ Passwords do not match")
            return
        
        # Create admin user
        admin = Customer(
            customer_id=uuid4(),
            email=email,
            name=name,
            phone=phone,
            hashed_password=get_password_hash(password),
            role="admin",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n" + "="*50)
        print("✅ ADMIN USER CREATED SUCCESSFULLY")
        print("="*50)
        print(f"Email: {admin.email}")
        print(f"Name: {admin.name}")
        print(f"Phone: {admin.phone or 'N/A'}")
        print(f"Role: {admin.role}")
        print(f"User ID: {admin.customer_id}")
        print("\nYou can now login with these credentials.")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
