import os
import random
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
from faker import Faker
from supabase import create_client, Client
from dotenv import load_dotenv

# --- Configuration ---
NUM_PROFILES = 100
NUM_ORDERS = 500

# --- Load Environment Variables ---
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in the .env file.")

# Initialize Faker and Supabase Admin Client
fake = Faker()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase admin client initialized.")


def generate_data():
    """Generates DataFrames for profiles, orders, and shipments."""
    print("--- Generating synthetic data in memory... ---")

    # 1. Profiles (formerly Customers)
    profiles_data = []
    for i in range(NUM_PROFILES):
        profiles_data.append(
            {
                "customer_id": fake.uuid4(),
                "email": f"classic_user_{i}@logimas.dev",
                "name": fake.name(),
                "address": json.dumps(
                    {"street": fake.street_address(), "city": fake.city()}
                ),
                "loyalty_tier": random.choice(["Bronze", "Silver", "Gold"]),
            }
        )
    profiles_df = pd.DataFrame(profiles_data)
    print(f"Generated {len(profiles_df)} profiles.")

    # 2. Orders
    orders_data = []
    products = [
        {
            "sku": f"PROD{i:04}",
            "name": f"Product {i}",
            "price": round(random.uniform(10, 200), 2),
        }
        for i in range(100)
    ]
    start_date = datetime.now(timezone.utc) - timedelta(days=90)

    for _ in range(NUM_ORDERS):
        order_date = start_date + timedelta(
            seconds=random.randint(0, 90 * 24 * 60 * 60)
        )

        # --- THIS IS THE FIX ---
        # Convert the Decimal types from Faker to standard floats before serializing.
        destination_data = {
            "lat": float(fake.latitude()),
            "lon": float(fake.longitude()),
        }

        orders_data.append(
            {
                "order_id": fake.uuid4(),
                "customer_id": random.choice(profiles_df["customer_id"]),
                "order_date": order_date.isoformat(),
                "order_total": round(random.uniform(20, 1000), 2),
                "items": json.dumps(random.sample(products, random.randint(1, 5))),
                "destination": json.dumps(destination_data),  # Use the converted data
                "status": random.choices(
                    ["delivered", "shipped", "processing"],
                    weights=[0.8, 0.15, 0.05],
                    k=1,
                )[0],
            }
        )
    orders_df = pd.DataFrame(orders_data)
    print(f"Generated {len(orders_df)} orders.")

    # 3. Shipments
    shipments_data = []
    warehouses = supabase.from_("warehouses").select("warehouse_id").execute().data
    vehicles = supabase.from_("vehicles").select("vehicle_id").execute().data

    for _, order in orders_df[
        orders_df["status"].isin(["shipped", "delivered"])
    ].iterrows():
        shipped_at = datetime.fromisoformat(order["order_date"]) + timedelta(
            hours=random.uniform(1, 24)
        )
        distance_km = random.uniform(5, 100)
        expected_arrival = shipped_at + timedelta(hours=distance_km / 40)
        shipments_data.append(
            {
                "shipment_id": fake.uuid4(),
                "order_id": order["order_id"],
                "origin_warehouse_id": random.choice(warehouses)["warehouse_id"],
                "vehicle_id": random.choice(vehicles)["vehicle_id"],
                "shipped_at": shipped_at.isoformat(),
                "expected_arrival": expected_arrival.isoformat(),
                "current_eta": expected_arrival.isoformat(),
                "status": order["status"],
                "distance_km": round(distance_km, 2),
            }
        )
    shipments_df = pd.DataFrame(shipments_data)
    print(f"Generated {len(shipments_df)} shipments.")

    return profiles_df, orders_df, shipments_df


def upload_data(df: pd.DataFrame, table_name: str):
    """Uploads a DataFrame to a Supabase table."""
    print(f"--- Uploading data to '{table_name}' table ---")
    records = df.to_dict(orient="records")
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        response = supabase.table(table_name).insert(batch).execute()
        if not response.data:
            print(
                f"!!! Error during batch upload to '{table_name}': {response.error or 'No data returned'}"
            )
            return
    print(f"Successfully uploaded {len(records)} records to '{table_name}'.")


def main():
    user_choice = input(
        "This script will clear existing profiles, orders, and shipments and re-seed them. Continue? (y/n): "
    ).lower()
    if user_choice != "y":
        print("Aborting.")
        return

    print("Clearing existing data...")
    supabase.from_("shipments").delete().neq(
        "shipment_id", "00000000-0000-0000-0000-000000000000"
    ).execute()
    supabase.from_("orders").delete().neq(
        "order_id", "00000000-0000-0000-0000-000000000000"
    ).execute()
    supabase.from_("profiles").delete().neq(
        "customer_id", "00000000-0000-0000-0000-000000000000"
    ).execute()

    profiles, orders, shipments = generate_data()
    upload_data(profiles, "profiles")
    upload_data(orders, "orders")
    upload_data(shipments, "shipments")

    print("\nClassic seeding process complete!")


if __name__ == "__main__":
    main()
