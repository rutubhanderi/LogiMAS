import os
import random
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
from faker import Faker
from supabase import create_client, Client
from dotenv import load_dotenv

NUM_PROFILES = 100
NUM_ORDERS = 500

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set.")

fake = Faker()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase admin client initialized.")


def generate_relational_data():
    print("--- Generating synthetic data... ---")

    profiles_data = [
        {
            "customer_id": fake.uuid4(),
            "email": f"classic_user_{i}@logimas.dev",
            "name": fake.name(),
            "address": json.dumps(
                {"street": fake.street_address(), "city": fake.city()}
            ),
            "loyalty_tier": random.choice(["Bronze", "Silver", "Gold"]),
        }
        for i in range(NUM_PROFILES)
    ]
    profiles_df = pd.DataFrame(profiles_data)
    print(f"Generated {len(profiles_df)} profiles.")

    orders_data = []
    shipments_data = []
    products = [{"sku": f"PROD{i:04}", "name": f"Product {i}"} for i in range(100)]
    start_date = datetime.now(timezone.utc) - timedelta(days=90)

    # Fetch warehouses and vehicles once
    warehouses = supabase.from_("warehouses").select("warehouse_id").execute().data
    vehicles = supabase.from_("vehicles").select("vehicle_id").execute().data

    for _ in range(NUM_ORDERS):
        order_date = start_date + timedelta(
            seconds=random.randint(0, 90 * 24 * 60 * 60)
        )
        order_status = random.choices(
            ["delivered", "shipped", "processing"], weights=[0.8, 0.15, 0.05], k=1
        )[0]

        order = {
            "order_id": fake.uuid4(),
            "customer_id": random.choice(profiles_df["customer_id"]),
            "order_date": order_date.isoformat(),
            "order_total": round(random.uniform(20, 1000), 2),
            "items": json.dumps(random.sample(products, random.randint(1, 5))),
            "destination": json.dumps(
                {"lat": float(fake.latitude()), "lon": float(fake.longitude())}
            ),
            "status": order_status,
        }
        orders_data.append(order)

        if order_status in ["shipped", "delivered"]:
            shipped_at = order_date + timedelta(hours=random.uniform(1, 24))
            distance_km = random.uniform(5, 100)
            expected_arrival = shipped_at + timedelta(hours=distance_km / 40)

            # --- THIS IS THE CRITICAL FIX ---
            actual_delivery = None
            if order_status == "delivered":
                # If delivered, set an actual delivery date close to the expected arrival
                actual_delivery = expected_arrival + timedelta(
                    minutes=random.randint(-120, 120)
                )

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
                    "actual_delivery_date": (
                        actual_delivery.isoformat() if actual_delivery else None
                    ),
                }
            )

    orders_df = pd.DataFrame(orders_data)
    shipments_df = pd.DataFrame(shipments_data)
    print(f"Generated {len(orders_df)} orders and {len(shipments_df)} shipments.")

    return profiles_df, orders_df, shipments_df


def upload_dataframe(df: pd.DataFrame, table_name: str):
    print(f"--- Uploading data to '{table_name}' table ---")
    records = df.to_dict(orient="records")
    for i in range(0, len(records), 500):
        batch = records[i : i + 500]
        # Replace NaN with None for database compatibility
        clean_batch = [
            {k: (None if pd.isna(v) else v) for k, v in record.items()}
            for record in batch
        ]
        response = supabase.table(table_name).insert(clean_batch).execute()
        if not response.data:
            print(
                f"!!! Error uploading to '{table_name}': {response.error or 'No data'}"
            )
            return
    print(f"Successfully uploaded {len(records)} records to '{table_name}'.")


def main():
    if (
        input(
            "This script will clear and re-seed profiles, orders, and shipments. Continue? (y/n): "
        ).lower()
        != "y"
    ):
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

    profiles_df, orders_df, shipments_df = generate_relational_data()

    upload_dataframe(profiles_df, "profiles")
    upload_dataframe(orders_df, "orders")
    upload_dataframe(shipments_df, "shipments")

    print("\nRelational data seeding complete!")
    print(
        "NOTE: The 'daily_on_time_rate' view will refresh automatically due to the trigger."
    )


if __name__ == "__main__":
    main()
