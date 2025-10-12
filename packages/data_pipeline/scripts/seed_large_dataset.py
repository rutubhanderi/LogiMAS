"""
Enhanced database seeding script with configurable data volumes
Optimized for large datasets with progress tracking
"""

import os
import random
import json
import uuid
from datetime import datetime, timedelta, timezone
import pandas as pd
from faker import Faker
from supabase import create_client, Client
from dotenv import load_dotenv
from tqdm import tqdm  # Progress bar

# Import configuration
from seed_config import *

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set.")

fake = Faker()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✓ Supabase client initialized")


def verify_rbac_setup():
    """Verify RBAC tables exist"""
    print("\n--- Verifying RBAC Setup ---")
    try:
        roles = supabase.from_("roles").select("*").execute()
        permissions = supabase.from_("permissions").select("*").execute()
        
        if not roles.data or not permissions.data:
            print("❌ RBAC tables not found. Run COMPLETE_SETUP.sql first!")
            return False
        
        print(f"✓ Roles: {len(roles.data)} found")
        print(f"✓ Permissions: {len(permissions.data)} found")
        return True
    except Exception as e:
        print(f"❌ Error checking RBAC: {str(e)}")
        return False


def seed_infrastructure():
    """Seed warehouses and vehicles"""
    print("\n--- Seeding Infrastructure ---")
    
    # Generate warehouses
    cities = [
        ('Los Angeles', 34.0522, -118.2437, 'SoCal'),
        ('San Francisco', 37.7749, -122.4194, 'NorCal'),
        ('San Diego', 32.7157, -117.1611, 'SoCal'),
        ('Sacramento', 38.5816, -121.4944, 'NorCal'),
        ('San Jose', 37.3382, -121.8863, 'NorCal'),
        ('Fresno', 36.7378, -119.7871, 'Central'),
        ('Oakland', 37.8044, -122.2712, 'NorCal'),
        ('Bakersfield', 35.3733, -119.0187, 'Central'),
        ('Anaheim', 33.8366, -117.9143, 'SoCal'),
        ('Riverside', 33.9533, -117.3962, 'SoCal'),
    ]
    
    warehouses_data = []
    for i in range(min(NUM_WAREHOUSES, len(cities))):
        city, lat, lon, region = cities[i]
        warehouses_data.append({
            # Let database generate warehouse_id automatically
            "name": f"{city} Distribution Center",
            "lat": lat,
            "lon": lon,
            "region": region
        })
    
    # Check if warehouses already exist
    existing = supabase.from_("warehouses").select("warehouse_id").execute()
    if existing.data and len(existing.data) >= NUM_WAREHOUSES:
        print(f"✓ Warehouses already exist: {len(existing.data)}")
        return existing.data
    
    response = supabase.from_("warehouses").insert(warehouses_data).execute()
    print(f"✓ Created {len(response.data)} warehouses")
    
    # Generate vehicles
    vehicle_types = ['Truck', 'Van', 'Box Truck', 'Semi-Truck']
    fuel_types = ['Diesel', 'Gasoline', 'Electric', 'Hybrid']
    
    vehicles_data = []
    for i in range(NUM_VEHICLES):
        v_type = random.choice(vehicle_types)
        capacity = random.randint(1000, 10000) if 'Truck' in v_type else random.randint(500, 2000)
        
        vehicles_data.append({
            # Let database generate vehicle_id automatically
            "vehicle_type": v_type,
            "capacity_kg": capacity,
            "capacity_volume_cm3": capacity * 2000,
            "fuel_type": random.choice(fuel_types),
            "status": random.choice(['available', 'in_use', 'maintenance'])
        })
    
    # Check if vehicles already exist
    existing = supabase.from_("vehicles").select("vehicle_id").execute()
    if existing.data and len(existing.data) >= NUM_VEHICLES:
        print(f"✓ Vehicles already exist: {len(existing.data)}")
        return response.data, existing.data
    
    v_response = supabase.from_("vehicles").insert(vehicles_data).execute()
    print(f"✓ Created {len(v_response.data)} vehicles")
    
    return response.data, v_response.data


def generate_customers():
    """Generate customer profiles"""
    print(f"\n--- Generating {NUM_CUSTOMERS} Customers ---")
    
    customers_data = []
    for i in tqdm(range(NUM_CUSTOMERS), desc="Generating customers"):
        customers_data.append({
            # Let database generate customer_id automatically
            "email": f"customer_{i}@logimas.dev",
            "name": fake.name(),
            "phone": fake.phone_number(),
            "address": json.dumps({
                "street": fake.street_address(),
                "city": fake.city(),
                "state": fake.state(),
                "zip": fake.zipcode()
            }),
            "loyalty_tier": random.choices(LOYALTY_TIERS, weights=LOYALTY_WEIGHTS, k=1)[0],
        })
    
    return pd.DataFrame(customers_data)


def generate_orders(customers_df):
    """Generate orders only"""
    print(f"\n--- Generating {NUM_ORDERS} Orders ---")
    
    # Generate product catalog
    products = [
        {
            "sku": f"PROD{i:04}",
            "name": f"Product {i}",
            "price": round(random.uniform(MIN_PRODUCT_PRICE, MAX_PRODUCT_PRICE), 2)
        }
        for i in range(NUM_PRODUCTS)
    ]
    
    orders_data = []
    start_date = datetime.now(timezone.utc) - timedelta(days=DAYS_OF_HISTORY)
    
    for i in tqdm(range(NUM_ORDERS), desc="Generating orders"):
        # Random order date within history
        order_date = start_date + timedelta(
            seconds=random.randint(0, DAYS_OF_HISTORY * 24 * 60 * 60)
        )
        
        # Determine order status
        order_status = random.choices(
            list(ORDER_STATUS_WEIGHTS.keys()),
            weights=list(ORDER_STATUS_WEIGHTS.values()),
            k=1
        )[0]
        
        # Select items for order
        num_items = random.randint(MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER)
        selected_items = random.sample(products, num_items)
        order_total = sum(item["price"] for item in selected_items)
        
        # Calculate delivery date if delivered
        actual_delivery = None
        if order_status == "delivered":
            delivery_time = order_date + timedelta(hours=random.uniform(24, 168))  # 1-7 days
            actual_delivery = delivery_time.isoformat()
        
        order = {
            # Let database generate order_id automatically
            "customer_id": random.choice(customers_df["customer_id"].tolist()),
            "order_date": order_date.isoformat(),
            "order_total": round(order_total, 2),
            "items": json.dumps(selected_items),
            "destination": json.dumps({
                "lat": float(fake.latitude()),
                "lon": float(fake.longitude())
            }),
            "status": order_status,
            "actual_delivery_date": actual_delivery
        }
        orders_data.append(order)
    
    orders_df = pd.DataFrame(orders_data)
    print(f"✓ Generated {len(orders_df)} orders")
    
    return orders_df


def generate_shipments(orders, warehouses, vehicles):
    """Generate shipments for shipped/delivered orders"""
    print(f"\n--- Generating Shipments ---")
    
    shipments_data = []
    
    for order in tqdm(orders, desc="Generating shipments"):
        if order["status"] in ["shipped", "delivered"]:
            order_date = datetime.fromisoformat(order["order_date"].replace('Z', '+00:00'))
            shipped_at = order_date + timedelta(hours=random.uniform(1, 48))
            distance_km = random.uniform(MIN_DISTANCE_KM, MAX_DISTANCE_KM)
            expected_arrival = shipped_at + timedelta(hours=distance_km / AVG_SPEED_KMH)
            
            shipments_data.append({
                # Let database generate shipment_id automatically
                "order_id": order["order_id"],
                "origin_warehouse_id": random.choice(warehouses)["warehouse_id"],
                "vehicle_id": random.choice(vehicles)["vehicle_id"],
                "shipped_at": shipped_at.isoformat(),
                "expected_arrival": expected_arrival.isoformat(),
                "current_eta": expected_arrival.isoformat(),
                "status": order["status"],
                "distance_km": round(distance_km, 2),
            })
    
    shipments_df = pd.DataFrame(shipments_data)
    print(f"✓ Generated {len(shipments_df)} shipments")
    
    return shipments_df


def upload_dataframe(df: pd.DataFrame, table_name: str):
    """Upload dataframe to Supabase in batches with progress bar"""
    print(f"\n--- Uploading to '{table_name}' ---")
    records = df.to_dict(orient="records")
    
    total_batches = (len(records) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i in tqdm(range(0, len(records), BATCH_SIZE), desc=f"Uploading {table_name}", total=total_batches):
        batch = records[i : i + BATCH_SIZE]
        clean_batch = [
            {k: (None if pd.isna(v) else v) for k, v in record.items()}
            for record in batch
        ]
        
        try:
            response = supabase.table(table_name).insert(clean_batch).execute()
            if not response.data:
                print(f"\n❌ Error uploading batch: {response.error}")
                return False
        except Exception as e:
            print(f"\n❌ Exception: {str(e)}")
            return False
    
    print(f"✓ Uploaded {len(records):,} records to '{table_name}'")
    return True


def main():
    """Main seeding function"""
    print("\n" + "="*60)
    print("LARGE DATASET SEEDING FOR LOGIMAS")
    print("="*60)
    
    # Show configuration
    print_config_summary()
    
    # Verify RBAC
    if not verify_rbac_setup():
        return
    
    # Confirm
    response = input("\nProceed with seeding? This will clear existing data. (y/n): ")
    if response.lower() != "y":
        print("Aborted.")
        return
    
    start_time = datetime.now()
    
    # Clear existing data
    print("\n--- Clearing Existing Data ---")
    try:
        supabase.from_("shipments").delete().neq("shipment_id", "00000000-0000-0000-0000-000000000000").execute()
        print("✓ Cleared shipments")
        supabase.from_("orders").delete().neq("order_id", "00000000-0000-0000-0000-000000000000").execute()
        print("✓ Cleared orders")
        supabase.from_("customers").delete().neq("customer_id", "00000000-0000-0000-0000-000000000000").execute()
        print("✓ Cleared customers")
    except Exception as e:
        print(f"⚠ Warning: {str(e)}")
    
    # Seed infrastructure
    warehouses, vehicles = seed_infrastructure()
    
    # Step 1: Generate and upload customers
    customers_df = generate_customers()
    success = upload_dataframe(customers_df, "customers")
    
    if not success:
        print("\n❌ Failed to upload customers")
        return
    
    # Step 2: Fetch uploaded customers with their database-generated IDs
    print("\n--- Fetching uploaded customers ---")
    uploaded_customers = supabase.from_("customers").select("customer_id").execute()
    customer_ids = [c["customer_id"] for c in uploaded_customers.data]
    print(f"✓ Retrieved {len(customer_ids)} customer IDs")
    
    # Create a dataframe with just customer IDs for order generation
    customers_id_df = pd.DataFrame({"customer_id": customer_ids})
    
    # Step 3: Generate and upload orders
    orders_df = generate_orders(customers_id_df)
    success = success and upload_dataframe(orders_df, "orders")
    
    if not success:
        print("\n❌ Failed to upload orders")
        return
    
    # Step 4: Fetch uploaded orders with their database-generated IDs
    print("\n--- Fetching uploaded orders ---")
    uploaded_orders = supabase.from_("orders").select("order_id, status, order_date").execute()
    print(f"✓ Retrieved {len(uploaded_orders.data)} order IDs")
    
    # Step 5: Generate and upload shipments
    shipments_df = generate_shipments(uploaded_orders.data, warehouses, vehicles)
    success = success and upload_dataframe(shipments_df, "shipments")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    if success:
        print("\n" + "="*60)
        print("✓ SEEDING COMPLETE!")
        print("="*60)
        print(f"Time taken: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"Customers: {len(customers_df):,}")
        print(f"Orders: {len(orders_df):,}")
        print(f"Shipments: {len(shipments_df):,}")
        print("="*60)
    else:
        print("\n❌ Seeding failed. Check errors above.")


if __name__ == "__main__":
    main()
