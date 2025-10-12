"""
Enhanced database seeding script with RBAC integration
This script seeds the database with sample data and properly assigns user roles
"""

import os
import random
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
from faker import Faker
from supabase import create_client, Client
from dotenv import load_dotenv

NUM_PROFILES = 100  # Keep customers reasonable
NUM_ORDERS = 2000   # Increased from 500 to 2000
NUM_SHIPMENTS_PER_ORDER = 1  # Each order gets 1 shipment

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set.")

fake = Faker()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase admin client initialized.")


def setup_test_users_with_roles():
    """Create test users and assign them roles"""
    print("\n--- Setting up test users with roles ---")
    
    test_users = [
        {
            "email": "admin@logimas.com",
            "password": "admin123",
            "role": "admin",
            "name": "Admin User"
        },
        {
            "email": "delivery@logimas.com",
            "password": "delivery123",
            "role": "delivery_person",
            "name": "Delivery Person"
        },
        {
            "email": "customer@logimas.com",
            "password": "customer123",
            "role": "customer",
            "name": "Test Customer"
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        print(f"Creating user: {user_data['email']}")
        
        # Check if user already exists
        existing = supabase.from_("auth.users").select("id, email").eq("email", user_data["email"]).execute()
        
        if existing.data:
            print(f"  User {user_data['email']} already exists")
            user_id = existing.data[0]["id"]
        else:
            # Note: Direct auth.users insert might not work
            # In production, use Supabase Auth API or dashboard to create users
            print(f"  Please create user {user_data['email']} manually in Supabase Dashboard")
            print(f"  Password: {user_data['password']}")
            continue
        
        # Assign role to user
        role_result = supabase.from_("roles").select("role_id").eq("role_name", user_data["role"]).execute()
        
        if role_result.data:
            role_id = role_result.data[0]["role_id"]
            
            # Assign role
            supabase.from_("user_roles").upsert({
                "user_id": user_id,
                "role_id": role_id
            }).execute()
            
            print(f"  ✓ Assigned role '{user_data['role']}' to {user_data['email']}")
            created_users.append({"user_id": user_id, "email": user_data["email"], "role": user_data["role"]})
    
    return created_users


def generate_relational_data():
    """Generate synthetic profiles, orders, and shipments"""
    print("\n--- Generating synthetic data... ---")

    profiles_data = [
        {
            "customer_id": fake.uuid4(),
            "email": f"customer_{i}@logimas.dev",
            "name": fake.name(),
            "phone": fake.phone_number(),
            "address": json.dumps(
                {"street": fake.street_address(), "city": fake.city(), "state": fake.state(), "zip": fake.zipcode()}
            ),
            "loyalty_tier": random.choice(["Bronze", "Silver", "Gold"]),
        }
        for i in range(NUM_PROFILES)
    ]
    profiles_df = pd.DataFrame(profiles_data)
    print(f"Generated {len(profiles_df)} customer profiles.")

    orders_data = []
    shipments_data = []
    products = [{"sku": f"PROD{i:04}", "name": f"Product {i}", "price": round(random.uniform(10, 200), 2)} for i in range(100)]
    start_date = datetime.now(timezone.utc) - timedelta(days=90)

    # Fetch warehouses and vehicles once
    warehouses = supabase.from_("warehouses").select("warehouse_id").execute().data
    vehicles = supabase.from_("vehicles").select("vehicle_id").execute().data

    if not warehouses or not vehicles:
        print("WARNING: No warehouses or vehicles found. Please seed those tables first.")
        return profiles_df, pd.DataFrame(), pd.DataFrame()

    for _ in range(NUM_ORDERS):
        order_date = start_date + timedelta(
            seconds=random.randint(0, 90 * 24 * 60 * 60)
        )
        order_status = random.choices(
            ["delivered", "shipped", "processing"], weights=[0.7, 0.2, 0.1], k=1
        )[0]

        selected_items = random.sample(products, random.randint(1, 5))
        order_total = sum(item["price"] for item in selected_items)

        order = {
            "order_id": fake.uuid4(),
            "customer_id": random.choice(profiles_df["customer_id"]),
            "order_date": order_date.isoformat(),
            "order_total": round(order_total, 2),
            "items": json.dumps(selected_items),
            "destination": json.dumps(
                {"lat": float(fake.latitude()), "lon": float(fake.longitude())}
            ),
            "status": order_status,
        }
        orders_data.append(order)

        if order_status in ["shipped", "delivered"]:
            shipped_at = order_date + timedelta(hours=random.uniform(1, 24))
            distance_km = random.uniform(5, 500)
            expected_arrival = shipped_at + timedelta(hours=distance_km / 60)

            actual_delivery = None
            if order_status == "delivered":
                actual_delivery = expected_arrival + timedelta(
                    minutes=random.randint(-120, 120)
                )
                # Update order with actual delivery date
                order["actual_delivery_date"] = actual_delivery.isoformat()

            shipments_data.append(
                {
                    "shipment_id": fake.uuid4(),
                    "order_id": order["order_id"],
                    "origin_warehouse_id": random.choice(warehouses)["warehouse_id"],
                    "vehicle_id": random.choice(vehicles)["vehicle_id"],
                    "shipped_at": shipped_at.isoformat(),
                    "expected_arrival": expected_arrival.isoformat(),
                    "current_eta": expected_arrival.isoformat(),
                    "status": order_status,
                    "distance_km": round(distance_km, 2),
                }
            )

    orders_df = pd.DataFrame(orders_data)
    shipments_df = pd.DataFrame(shipments_data)
    print(f"Generated {len(orders_df)} orders and {len(shipments_df)} shipments.")

    return profiles_df, orders_df, shipments_df


def upload_dataframe(df: pd.DataFrame, table_name: str):
    """Upload dataframe to Supabase table in batches"""
    print(f"\n--- Uploading data to '{table_name}' table ---")
    records = df.to_dict(orient="records")
    
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        # Replace NaN with None for database compatibility
        clean_batch = [
            {k: (None if pd.isna(v) else v) for k, v in record.items()}
            for record in batch
        ]
        
        try:
            response = supabase.table(table_name).insert(clean_batch).execute()
            if not response.data:
                print(f"!!! Error uploading batch to '{table_name}': {response.error or 'No data'}")
                return False
            print(f"  Uploaded batch {i//batch_size + 1} ({len(batch)} records)")
        except Exception as e:
            print(f"!!! Exception uploading to '{table_name}': {str(e)}")
            return False
    
    print(f"✓ Successfully uploaded {len(records)} records to '{table_name}'.")
    return True


def verify_rbac_setup():
    """Verify RBAC tables and data"""
    print("\n--- Verifying RBAC Setup ---")
    
    # Check roles
    roles = supabase.from_("roles").select("*").execute()
    print(f"✓ Roles: {len(roles.data)} found")
    for role in roles.data:
        print(f"  - {role['role_name']}: {role['description']}")
    
    # Check permissions
    permissions = supabase.from_("permissions").select("*").execute()
    print(f"✓ Permissions: {len(permissions.data)} found")
    
    # Check role-permission mappings
    mappings = supabase.from_("role_permissions").select("*").execute()
    print(f"✓ Role-Permission Mappings: {len(mappings.data)} found")
    
    # Check user roles
    user_roles = supabase.from_("user_roles").select("*").execute()
    print(f"✓ User-Role Assignments: {len(user_roles.data)} found")
    
    return True


def main():
    """Main seeding function"""
    print("=" * 60)
    print("DATABASE SEEDING WITH RBAC INTEGRATION")
    print("=" * 60)
    
    # Verify RBAC is set up
    if not verify_rbac_setup():
        print("\n!!! RBAC tables not found. Please run migrations first.")
        return
    
    # Ask for confirmation
    response = input("\nThis script will clear and re-seed profiles, orders, and shipments.\nContinue? (y/n): ")
    if response.lower() != "y":
        print("Aborting.")
        return

    # Clear existing data
    print("\n--- Clearing existing data ---")
    try:
        supabase.from_("shipments").delete().neq("shipment_id", "00000000-0000-0000-0000-000000000000").execute()
        print("✓ Cleared shipments")
        
        supabase.from_("orders").delete().neq("order_id", "00000000-0000-0000-0000-000000000000").execute()
        print("✓ Cleared orders")
        
        supabase.from_("customers").delete().neq("customer_id", "00000000-0000-0000-0000-000000000000").execute()
        print("✓ Cleared customers")
    except Exception as e:
        print(f"Warning: Error clearing data: {str(e)}")

    # Generate and upload data
    profiles_df, orders_df, shipments_df = generate_relational_data()

    if len(orders_df) == 0:
        print("\n!!! Cannot proceed without warehouses and vehicles. Please seed those first.")
        return

    success = True
    success = success and upload_dataframe(profiles_df, "customers")
    success = success and upload_dataframe(orders_df, "orders")
    success = success and upload_dataframe(shipments_df, "shipments")

    if success:
        print("\n" + "=" * 60)
        print("✓ DATABASE SEEDING COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Create test users in Supabase Dashboard:")
        print("   - admin@logimas.com (password: admin123)")
        print("   - delivery@logimas.com (password: delivery123)")
        print("   - customer@logimas.com (password: customer123)")
        print("\n2. Run the role assignment SQL:")
        print("   See output above for SQL commands")
        print("\n3. Test the application with different roles")
    else:
        print("\n!!! Seeding encountered errors. Please check the logs above.")


if __name__ == "__main__":
    main()
