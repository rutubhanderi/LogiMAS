"""
Generates realistic fake datasets for all tables using Faker and directly ingests them into Supabase.

Tables covered:
- customers
- warehouses
- vehicles
- packaging_types
- orders
- shipments
- inventory
- fuel_prices
- vehicle_telemetry
- documents (basic text, no embeddings)
"""
from __future__ import annotations

import json
import math
import random
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from faker import Faker
from dotenv import load_dotenv
from supabase import create_client, Client

# --- Configuration ---
# Set the desired number of records for scalable tables
NUM_CUSTOMERS = 1000
NUM_ORDERS = 1000
NUM_VEHICLES = 50
NUM_DOCUMENTS = 200
TELEMETRY_PER_VEHICLE = 20
INVENTORY_PER_WAREHOUSE = 50

# scripts now live under src/scripts/, so project root is two levels up
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ENV_PATH = BASE_DIR / ".env"
BATCH_SIZE = 500


# --- Faker and Random Initialization ---
fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

# --- Environment Loading and Supabase Client Initialization ---
load_dotenv(dotenv_path=ENV_PATH)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials in .env file")
    print("   Required variables:")
    print("   - NEXT_PUBLIC_SUPABASE_URL")
    print("   - SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL.strip(), SUPABASE_KEY.strip())


# --- Helper Functions ---
def rand_lat_lon_for_city(city: str) -> tuple[float, float]:
    """Generates random latitude and longitude for a given city."""
    boxes = {
        "Delhi": (28.40, 28.90, 76.80, 77.40),
        "Mumbai": (18.80, 19.30, 72.70, 72.95),
        "Bangalore": (12.80, 13.20, 77.45, 77.75),
        "Chennai": (12.90, 13.20, 80.10, 80.35),
        "Ahmedabad": (22.90, 23.20, 72.40, 72.80),
        "Hyderabad": (17.20, 17.60, 78.30, 78.60),
        "Pune": (18.40, 18.70, 73.70, 73.95),
        "Kolkata": (22.45, 22.70, 88.25, 88.45),
    }
    if city not in boxes:
        from random import uniform
        return uniform(-90, 90), uniform(-180, 180)
    lat_min, lat_max, lon_min, lon_max = boxes[city]
    return (
        round(random.uniform(lat_min, lat_max), 6),
        round(random.uniform(lon_min, lon_max), 6),
    )

def batched(rows: List[Dict[str, Any]], size: int = BATCH_SIZE):
    """Batch data for efficient processing"""
    for i in range(0, len(rows), size):
        yield rows[i : i + size]

# --- Data Generation Functions ---
def gen_customers(n: int = NUM_CUSTOMERS) -> List[Dict[str, Any]]:
    rows = []
    roles = ["customer", "customer", "customer", "delivery_guy"]  # bias toward customer
    for _ in range(n):
        cust_id = str(uuid4())
        address = {
            "line1": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "postal_code": fake.postcode(),
            "country": "IN",
        }
        rows.append(
            {
                "customer_id": cust_id,
                "email": fake.unique.ascii_safe_email(),
                "name": fake.name(),
                "phone": fake.msisdn()[:10],
                "address": address,
                "role": random.choice(roles),
                "hashed_password": "password@123",  # Common password (plaintext for demo; in production, hash properly)
                "created_at": datetime.utcnow().isoformat(),
                "last_login": None,
                "is_active": True,
            }
        )
    # Ensure we have at least 1 delivery_guy
    if not any(r["role"] == "delivery_guy" for r in rows):
        rows[0]["role"] = "delivery_guy"
    return rows


def gen_warehouses() -> List[Dict[str, Any]]:
    cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Ahmedabad"]
    rows = []
    for c in cities:
        wid = str(uuid4())
        lat, lon = rand_lat_lon_for_city(c)
        rows.append(
            {
                "warehouse_id": wid,
                "name": f"{c} {random.choice(['Central', 'Hub', 'North', 'South'])}",
                "lat": lat,
                "lon": lon,
                "region": c,
            }
        )
    return rows


def gen_vehicles(n: int = NUM_VEHICLES) -> List[Dict[str, Any]]:
    vehicle_types = ["Truck", "Van", "Bike"]
    fuel_types = ["Diesel", "Petrol", "CNG", "EV"]
    statuses = ["active", "maintenance", "inactive"]
    rows = []
    for _ in range(n):
        rows.append(
            {
                "vehicle_id": str(uuid4()),
                "vehicle_type": random.choice(vehicle_types),
                "capacity_kg": round(random.uniform(50, 5000), 2),
                "capacity_volume_cm3": round(random.uniform(5e4, 5e6), 2),
                "fuel_type": random.choice(fuel_types),
                "status": random.choice(statuses),
            }
        )
    return rows


def gen_packaging_types() -> List[Dict[str, Any]]:
    presets = [
        ("Small Box", 20, 20, 20, 30),
        ("Medium Box", 40, 30, 25, 60),
        ("Large Box", 60, 40, 40, 120),
        ("Envelope", 30, 20, 1, 10),
    ]
    rows = []
    for name, l, w, h, cost in presets:
        rows.append(
            {
                "packaging_id": str(uuid4()),
                "name": name,
                "length_cm": l,
                "width_cm": w,
                "height_cm": h,
                # volume_cm3 computed in DB
                "cost_per_unit": cost,
            }
        )
    return rows


def gen_orders(customers, n: int = NUM_ORDERS) -> List[Dict[str, Any]]:
    rows = []
    for _ in range(n):
        cust = random.choice(customers)
        order_date = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        eta_days = random.randint(1, 7)
        delivered = random.choice([True, False, False])
        dest_city = random.choice(["Delhi", "Mumbai", "Bangalore", "Chennai", "Ahmedabad", "Pune", "Kolkata"])
        dest_lat, dest_lon = rand_lat_lon_for_city(dest_city)
        rows.append(
            {
                "order_id": str(uuid4()),
                "customer_id": cust["customer_id"],
                "order_date": order_date.isoformat(),
                "order_total": round(random.uniform(200, 20000), 2),
                "items": [
                    {
                        "sku": fake.unique.bothify(text="SKU-####"),
                        "name": fake.word().title(),
                        "qty": random.randint(1, 4),
                        "price": round(random.uniform(50, 5000), 2),
                    }
                ],
                "destination": {
                    "address": fake.street_address(),
                    "city": dest_city,
                    "lat": dest_lat,
                    "lon": dest_lon,
                    "postal_code": fake.postcode(),
                },
                "status": random.choice(["pending", "in-transit", "delivered", "cancelled"]),
                "estimated_delivery_date": (order_date + timedelta(days=eta_days)).isoformat(),
                "actual_delivery_date": (order_date + timedelta(days=eta_days + random.randint(0, 2))).isoformat() if delivered else None,
            }
        )
    return rows


def gen_shipments(orders, warehouses, vehicles) -> List[Dict[str, Any]]:
    rows = []
    for o in orders:
        if random.random() < 0.8:
            wh = random.choice(warehouses)
            vehicle = random.choice(vehicles)
            shipped_at = datetime.fromisoformat(o["order_date"]) + timedelta(hours=random.randint(1, 24))
            status = random.choice(["pending", "in-transit", "delivered"])
            expected = shipped_at + timedelta(days=random.randint(1, 5))
            eta = expected - timedelta(hours=random.randint(0, 24))
            rows.append(
                {
                    "shipment_id": str(uuid4()),
                    "order_id": o["order_id"],
                    "origin_warehouse_id": wh["warehouse_id"],
                    "vehicle_id": vehicle["vehicle_id"],
                    "shipped_at": shipped_at.isoformat(),
                    "expected_arrival": expected.isoformat(),
                    "current_eta": eta.isoformat(),
                    "status": status,
                    "distance_km": round(random.uniform(10, 2500), 2),
                }
            )
    return rows


def gen_inventory(warehouses, n_per_wh: int = INVENTORY_PER_WAREHOUSE) -> List[Dict[str, Any]]:
    rows = []
    for wh in warehouses:
        for _ in range(n_per_wh):
            rows.append(
                {
                    "inventory_id": str(uuid4()),
                    "warehouse_id": wh["warehouse_id"],
                    "sku": fake.unique.bothify(text="SKU-#####"),
                    "product_name": fake.word().title(),
                    "qty_on_hand": random.randint(0, 500),
                    "reorder_point": random.randint(10, 150),
                }
            )
    return rows


def gen_fuel_prices() -> List[Dict[str, Any]]:
    fuel_types = ["Diesel", "Petrol", "CNG", "EV"]
    rows = []
    for ft in fuel_types:
        rows.append(
            {
                "fuel_type": ft,
                "cost_per_liter": round(random.uniform(60, 130), 2),
                "last_updated": datetime.utcnow().isoformat(),
            }
        )
    return rows


def gen_vehicle_telemetry(vehicles, per_vehicle: int = TELEMETRY_PER_VEHICLE) -> List[Dict[str, Any]]:
    rows = []
    now = datetime.utcnow()
    for v in vehicles:
        ts = now - timedelta(hours=per_vehicle)
        from random import choice, uniform
        city = choice(["Delhi", "Mumbai", "Bangalore", "Chennai", "Ahmedabad", "Kolkata", "Pune"])
        lat, lon = rand_lat_lon_for_city(city)
        for i in range(per_vehicle):
            rows.append(
                {
                    "vehicle_id": v["vehicle_id"],
                    "ts": (ts + timedelta(hours=i)).isoformat(),
                    "lat": lat + uniform(-0.15, 0.15),
                    "lon": lon + uniform(-0.15, 0.15),
                    "speed_kmph": round(abs(random.gauss(40, 15)), 2),
                    "fuel_pct": round(max(0, min(100, 80 - i * (100 / per_vehicle) + uniform(-2, 2))), 2),
                    "cargo_temp": round(20 + uniform(-5, 8), 2),
                }
            )
    return rows


def gen_documents(n: int = NUM_DOCUMENTS) -> List[Dict[str, Any]]:
    rows = []
    for i in range(n):
        rows.append(
            {
                "doc_id": str(uuid4()),
                "source_type": random.choice(["order", "shipment", "policy", "faq"]),
                "source_id": str(uuid4()),
                "region_id": random.choice(["north", "south", "east", "west"]),
                "ts": datetime.utcnow().isoformat(),
                "chunk_index": 0,
                "text_snippet": fake.paragraph(nb_sentences=5),
                "embedding_model": "text-embedding-3-small",
            }
        )
    return rows


# --- Seeding Functions ---
def safe_upsert(table: str, rows: List[Dict[str, Any]], on_conflict: str | None = None):
    """Safe upsert with error handling and schema validation"""
    if not rows:
        return

    # Get table schema to filter valid columns
    try:
        res = supabase.table(table).select("*").limit(1).execute()
        valid_columns = set(res.data[0].keys()) if res.data else set()
    except Exception as e:
        print(f"⚠️  Could not get schema for {table}: {str(e)}")
        valid_columns = set()

    for chunk in batched(rows):
        # Filter out invalid columns
        filtered_chunk = []
        for row in chunk:
            filtered_row = {
                k: v for k, v in row.items() if not valid_columns or k in valid_columns
            }
            filtered_chunk.append(filtered_row)

        try:
            if on_conflict:
                res = (
                    supabase.table(table)
                    .upsert(filtered_chunk, on_conflict=on_conflict)
                    .execute()
                )
            else:
                res = supabase.table(table).upsert(filtered_chunk).execute()

            if getattr(res, "error", None):
                print(f"❌ Error upserting into {table}: {res.error}")
                print(
                    f"   First failed row: {json.dumps(filtered_chunk[0], indent=2) if filtered_chunk else '[]'}"
                )
                # Try to continue with next batch
                continue
        except Exception as e:
            print(f"❌ Error upserting into {table}: {str(e)}")
            continue


def seed_customers(customers: List[Dict[str, Any]]):
    """Special handling for customer seeding"""
    if not customers:
        return
    # Get a list of valid columns from the table to avoid sending unknown fields
    try:
        schema_res = supabase.table("customers").select("*").limit(1).execute()
        valid_columns = set(schema_res.data[0].keys()) if schema_res.data else set()
    except Exception as e:
        print(f"⚠️  Could not get schema for customers: {str(e)}")
        valid_columns = set()

    for customer in customers:
        try:
            # Filter out any keys not present in the table schema
            if valid_columns:
                filtered = {k: v for k, v in customer.items() if k in valid_columns}
            else:
                filtered = dict(customer)

            # First try normal upsert by customer_id
            res = (
                supabase.table("customers")
                .upsert(filtered, on_conflict="customer_id")
                .execute()
            )

            if getattr(res, "error", None):
                # Handle email conflicts (unique constraint)
                if (
                    getattr(res, "error", None)
                    and getattr(res.error, "code", "") == "23505"
                    and "email" in str(res.error)
                ):
                    # Find existing customer with this email
                    existing = (
                        supabase.table("customers")
                        .select("customer_id")
                        .eq("email", customer.get("email"))
                        .execute()
                    )

                    if existing.data:
                        # Update existing record instead
                        filtered["customer_id"] = existing.data[0]["customer_id"]
                        res = (
                            supabase.table("customers")
                            .upsert(filtered, on_conflict="customer_id")
                            .execute()
                        )

                if getattr(res, "error", None):
                    print(
                        f"❌ Failed to upsert customer {customer.get('email')}: {res.error}"
                    )
        except Exception as e:
            print(f"❌ Error processing customer {customer.get('email')}: {str(e)}")


def main():
    """Main seeding function with proper order and error handling"""
    print("\n--- Generating Data ---")
    customers = gen_customers()
    warehouses = gen_warehouses()
    vehicles = gen_vehicles()
    packaging_types = gen_packaging_types()
    orders = gen_orders(customers)
    shipments = gen_shipments(orders, warehouses, vehicles)
    inventory = gen_inventory(warehouses)
    fuel_prices = gen_fuel_prices()
    telemetry = gen_vehicle_telemetry(vehicles)
    documents = gen_documents()

    print("\n--- Seeding Base Tables ---")
    seed_customers(customers)
    safe_upsert("warehouses", warehouses, on_conflict="warehouse_id")
    safe_upsert("vehicles", vehicles, on_conflict="vehicle_id")
    safe_upsert("packaging_types", packaging_types, on_conflict="packaging_id")
    safe_upsert("fuel_prices", fuel_prices, on_conflict="fuel_type")

    print("\n--- Seeding Dependent Tables ---")
    safe_upsert("orders", orders, on_conflict="order_id")
    safe_upsert("shipments", shipments, on_conflict="shipment_id")
    safe_upsert("inventory", inventory, on_conflict="inventory_id")

    print("\n--- Seeding Telemetry and Documents ---")
    safe_upsert("vehicle_telemetry", telemetry)
    safe_upsert("documents", documents, on_conflict="doc_id")

    print("\n✅ Supabase seeding complete!")


if __name__ == "__main__":
    main()