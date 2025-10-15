import os
import random
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
from faker import Faker
from supabase import create_client, Client
from dotenv import load_dotenv

# --- CONFIGURATION ---
NUM_CUSTOMERS = 100
NUM_ORDERS = 500

# --- INITIALIZATION ---
# Assumes your .env file is three directories above the script's location
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in your .env file.")

fake = Faker()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase admin client initialized.")


def generate_relational_data():
    """Generates synthetic data for customers, orders, and shipments."""
    print("--- Generating synthetic data... ---")

    # 1. Generate Customers
    customers_data = [
        {
            "customer_id": fake.uuid4(),
            "email": f"customer_{i}@example.com",
            "name": fake.name(),
            "address": json.dumps(
                {"street": fake.street_address(), "city": fake.city(), "country": fake.country()}
            ),
            "loyalty_tier": random.choice(["Bronze", "Silver", "Gold", "Platinum"]),
            "role": "user",  # Assign a default role for backend RBAC
        }
        for i in range(NUM_CUSTOMERS)
    ]
    customers_df = pd.DataFrame(customers_data)
    print(f"Generated {len(customers_df)} customers.")

    # 2. Generate Orders and Shipments
    orders_data = []
    shipments_data = []
    products = [{"sku": f"PROD{i:04}", "name": f"Product Name {i}"} for i in range(100)]
    start_date = datetime.now(timezone.utc) - timedelta(days=90)

    # Fetch foreign keys once to avoid multiple DB calls
    try:
        warehouses = supabase.from_("warehouses").select("warehouse_id").execute().data
        vehicles = supabase.from_("vehicles").select("vehicle_id").execute().data
        if not warehouses or not vehicles:
            print("!!! WARNING: No warehouses or vehicles found in the database. Shipments cannot be generated.")
            print("!!! Please seed warehouses and vehicles before running this script.")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame() # Return empty dataframes
    except Exception as e:
        print(f"!!! Error fetching warehouses or vehicles: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


    for _ in range(NUM_ORDERS):
        order_date = start_date + timedelta(
            seconds=random.randint(0, 90 * 24 * 60 * 60)
        )
        order_status = random.choices(
            ["delivered", "shipped", "processing"], weights=[0.8, 0.15, 0.05], k=1
        )[0]

        # Initialize delivery date as None
        actual_delivery_date = None

        # Create shipment record if order is shipped or delivered
        if order_status in ["shipped", "delivered"]:
            shipped_at = order_date + timedelta(hours=random.uniform(1, 24))
            distance_km = random.uniform(5, 100)
            expected_arrival = shipped_at + timedelta(hours=(distance_km / 40) + 1) # Avg speed 40km/h

            # If delivered, set the actual delivery date for the order
            if order_status == "delivered":
                actual_delivery_date = expected_arrival + timedelta(minutes=random.randint(-120, 120))

            shipments_data.append(
                {
                    "shipment_id": fake.uuid4(),
                    "order_id": None, # Will be set after order is created
                    "origin_warehouse_id": random.choice(warehouses)["warehouse_id"],
                    "vehicle_id": random.choice(vehicles)["vehicle_id"],
                    "shipped_at": shipped_at.isoformat(),
                    "expected_arrival": expected_arrival.isoformat(),
                    "current_eta": expected_arrival.isoformat(),
                    "status": order_status,
                    "distance_km": round(distance_km, 2),
                }
            )
        
        order = {
            "order_id": fake.uuid4(),
            "customer_id": random.choice(customers_df["customer_id"]),
            "order_date": order_date.isoformat(),
            "order_total": round(random.uniform(20, 1000), 2),
            "items": json.dumps(random.sample(products, random.randint(1, 5))),
            "destination": json.dumps(
                {"lat": float(fake.latitude()), "lon": float(fake.longitude())}
            ),
            "status": order_status,
            "actual_delivery_date": actual_delivery_date.isoformat() if actual_delivery_date else None,
        }
        orders_data.append(order)

        # Link the last created shipment to this order
        if order_status in ["shipped", "delivered"]:
            shipments_data[-1]["order_id"] = order["order_id"]


    orders_df = pd.DataFrame(orders_data)
    shipments_df = pd.DataFrame(shipments_data)
    print(f"Generated {len(orders_df)} orders and {len(shipments_df)} shipments.")

    return customers_df, orders_df, shipments_df


def upload_dataframe(df: pd.DataFrame, table_name: str):
    """Uploads a pandas DataFrame to a Supabase table in batches."""
    if df.empty:
        print(f"--- DataFrame for '{table_name}' is empty. Skipping upload. ---")
        return

    print(f"--- Uploading data to '{table_name}' table ---")
    records = df.to_dict(orient="records")
    
    # Supabase client has a max payload size, so we batch inserts
    for i in range(0, len(records), 500):
        batch = records[i : i + 500]
        # Replace pandas NaN/NaT with Python's None for database compatibility
        clean_batch = [
            {k: (None if pd.isna(v) else v) for k, v in record.items()}
            for record in batch
        ]
        try:
            response = supabase.table(table_name).insert(clean_batch).execute()
        except Exception as e:
            print(f"!!! An exception occurred uploading to '{table_name}': {e}")
            return
            
    print(f"Successfully uploaded {len(records)} records to '{table_name}'.")


def main():
    """Main function to clear and seed the database."""
    if (
        input(
            "This script will DELETE and re-seed customers, orders, and shipments. Are you sure? (y/n): "
        ).lower()
        != "y"
    ):
        print("Aborting.")
        return

    print("--- Clearing existing data... ---")
    # Delete from tables in the correct order to respect foreign key constraints
    supabase.from_("shipments").delete().neq("shipment_id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.from_("orders").delete().neq("order_id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.from_("customers").delete().neq("customer_id", "00000000-0000-0000-0000-000000000000").execute()
    print("--- Data cleared. ---")

    customers_df, orders_df, shipments_df = generate_relational_data()

    upload_dataframe(customers_df, "customers")
    upload_dataframe(orders_df, "orders")
    upload_dataframe(shipments_df, "shipments")

    print("\n✅ Relational data seeding complete!")


if __name__ == "__main__":
    main()