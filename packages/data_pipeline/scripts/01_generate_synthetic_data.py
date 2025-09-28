import pandas as pd
import numpy as np
from faker import Faker
import random
import json
from datetime import datetime, timedelta
import os

# --- Configuration ---
NUM_CUSTOMERS = 1000
NUM_VEHICLES = 50
NUM_ORDERS = 5000
NUM_WAREHOUSES = 3

# Geographic bounds for realism (e.g., within Los Angeles County)
LAT_BOUNDS = (34.0, 34.2)
LON_BOUNDS = (-118.6, -118.3)
REGION_NAME = "SoCal"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "generated")
os.makedirs(OUTPUT_DIR, exist_ok=True)

fake = Faker()

print("Starting synthetic data generation...")

# --- 1. Warehouses ---
print("Generating warehouses...")
warehouses_data = [
    {
        "warehouse_id": i + 1,
        "name": f"{REGION_NAME} Distribution Center {chr(65+i)}",
        "lat": round(random.uniform(*LAT_BOUNDS), 6),
        "lon": round(random.uniform(*LON_BOUNDS), 6),
        "region": REGION_NAME,
    }
    for i in range(NUM_WAREHOUSES)
]
warehouses_df = pd.DataFrame(warehouses_data)
warehouses_df.to_csv(os.path.join(OUTPUT_DIR, "warehouses.csv"), index=False)
print(f"Generated {len(warehouses_df)} warehouses.")

# --- 2. Customers ---
print("Generating customers...")
customers_data = []
for _ in range(NUM_CUSTOMERS):
    address = {
        "street": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip_code": fake.zipcode(),
    }
    customers_data.append(
        {
            "customer_id": fake.uuid4(),
            "email": fake.unique.email(),
            "name": fake.name(),
            "phone": fake.phone_number(),
            "address": json.dumps(address),
            "loyalty_tier": random.choice(["Bronze", "Silver", "Gold", "Platinum"]),
        }
    )
customers_df = pd.DataFrame(customers_data)
customers_df.to_csv(os.path.join(OUTPUT_DIR, "customers.csv"), index=False)
print(f"Generated {len(customers_df)} customers.")

# --- 3. Vehicles ---
print("Generating vehicles...")
vehicles_data = []
for _ in range(NUM_VEHICLES):
    v_type = random.choice(["Van", "Small Truck", "Large Truck"])
    capacity_map = {
        "Van": (500, 4_000_000),
        "Small Truck": (2000, 15_000_000),
        "Large Truck": (10000, 80_000_000),
    }
    vehicles_data.append(
        {
            "vehicle_id": fake.uuid4(),
            "vehicle_type": v_type,
            "capacity_kg": capacity_map[v_type][0],
            "capacity_volume_cm3": capacity_map[v_type][1],
            "fuel_type": random.choice(["Diesel", "Gasoline", "Electric"]),
            "status": "idle",
        }
    )
vehicles_df = pd.DataFrame(vehicles_data)
vehicles_df.to_csv(os.path.join(OUTPUT_DIR, "vehicles.csv"), index=False)
print(f"Generated {len(vehicles_df)} vehicles.")

# --- 4. Products (in-memory) ---
products = [
    {
        "sku": f"PROD{i:04}",
        "name": f"Product {i}",
        "price": round(random.uniform(10, 200), 2),
    }
    for i in range(100)
]

# --- 5. Orders & Shipments ---
print("Generating orders and shipments...")
orders_data = []
shipments_data = []
start_date = datetime.now() - timedelta(days=90)

for i in range(NUM_ORDERS):
    order_date = start_date + timedelta(seconds=random.randint(0, 90 * 24 * 60 * 60))
    order_items = random.sample(products, random.randint(1, 5))
    order_total = sum(item["price"] for item in order_items)
    destination = {
        "lat": round(random.uniform(*LAT_BOUNDS), 6),
        "lon": round(random.uniform(*LON_BOUNDS), 6),
        "address": fake.street_address(),
    }
    order_id = fake.uuid4()
    status = random.choices(
        ["delivered", "shipped", "processing"], weights=[0.8, 0.15, 0.05], k=1
    )[0]

    # Initialize date fields as None
    est_delivery = None
    actual_delivery = None

    if status in ["shipped", "delivered"]:
        shipped_at = order_date + timedelta(hours=random.uniform(1, 24))
        distance_km = random.uniform(5, 100)
        travel_time_hours = distance_km / 40
        expected_arrival = shipped_at + timedelta(hours=travel_time_hours)
        est_delivery = expected_arrival

        current_eta = expected_arrival
        if status == "shipped":
            current_eta += timedelta(minutes=random.randint(-30, 30))
        elif status == "delivered":
            actual_delivery = expected_arrival + timedelta(
                minutes=random.randint(-30, 30)
            )

        shipments_data.append(
            {
                "shipment_id": fake.uuid4(),
                "order_id": order_id,
                "origin_warehouse_id": random.choice(warehouses_df["warehouse_id"]),
                "vehicle_id": random.choice(vehicles_df["vehicle_id"]),
                "shipped_at": shipped_at,
                "expected_arrival": expected_arrival,
                "current_eta": current_eta,
                "status": status,
                "distance_km": round(distance_km, 2),
            }
        )

    orders_data.append(
        {
            "order_id": order_id,
            "customer_id": random.choice(customers_df["customer_id"]),
            "order_date": order_date,
            "order_total": round(order_total, 2),
            "items": json.dumps(order_items),
            "destination": json.dumps(destination),
            "status": status,
            "estimated_delivery_date": est_delivery,
            "actual_delivery_date": actual_delivery,
        }
    )

# FIX: Convert dataframes and handle NaT (Not a Time) from pandas gracefully
orders_df = pd.DataFrame(orders_data)
orders_df["estimated_delivery_date"] = pd.to_datetime(
    orders_df["estimated_delivery_date"]
).where(pd.notnull(orders_df["estimated_delivery_date"]), None)
orders_df["actual_delivery_date"] = pd.to_datetime(
    orders_df["actual_delivery_date"]
).where(pd.notnull(orders_df["actual_delivery_date"]), None)

shipments_df = pd.DataFrame(shipments_data)

orders_df.to_csv(os.path.join(OUTPUT_DIR, "orders.csv"), index=False)
shipments_df.to_csv(os.path.join(OUTPUT_DIR, "shipments.csv"), index=False)
print(f"Generated {len(orders_df)} orders and {len(shipments_df)} shipments.")

# --- 6. Sample RAG data ---
print("Generating sample incident reports for RAG...")
# (The rest of the script is the same)
incident_reports_dir = os.path.join(
    os.path.dirname(__file__), "..", "data", "raw", "incident_reports"
)
report_text = """
INCIDENT REPORT
Date: 2025-09-27 14:30:00
Region: SoCal
Location: I-405 Northbound near Exit 45
Reported by: Field Agent 7
Details:
A multi-vehicle collision has resulted in the complete shutdown of all northbound lanes on the I-405. 
Traffic is being diverted onto Sepulveda Blvd. 
Estimated clearance time is 3-4 hours. 
Heavy congestion is expected to impact all surrounding routes.
LogiMAS vehicles with route plans including this segment must be rerouted immediately.
Recommended alternate: Route 101 via Topanga Canyon Blvd, although expect moderate delays.
"""
with open(os.path.join(incident_reports_dir, "20250927_I405_shutdown.txt"), "w") as f:
    f.write(report_text)
print("Generated sample incident report.")

print("\nSynthetic data generation complete!")
