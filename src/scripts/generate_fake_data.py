"""
Generate realistic fake datasets for all tables using Faker.
Outputs JSON files under data/ directory.

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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from faker import Faker

# scripts now live under src/scripts/, so project root is two levels up
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

# Helpers

def rand_lat_lon_for_city(city: str) -> tuple[float, float]:
    # Rough bounding boxes for a few Indian cities
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


def write_json(name: str, rows: List[Dict[str, Any]]):
    (DATA_DIR / f"{name}.json").write_text(
        json.dumps(rows, default=str, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def gen_customers(n: int = 150) -> List[Dict[str, Any]]:
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


def gen_vehicles(n: int = 30) -> List[Dict[str, Any]]:
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


def gen_orders(customers, n: int = 5200) -> List[Dict[str, Any]]:
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


def gen_inventory(warehouses, n_per_wh: int = 25) -> List[Dict[str, Any]]:
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


def gen_vehicle_telemetry(vehicles, per_vehicle: int = 20) -> List[Dict[str, Any]]:
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


def gen_documents(n: int = 10) -> List[Dict[str, Any]]:
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


if __name__ == "__main__":
    customers = gen_customers(150)
    warehouses = gen_warehouses()
    vehicles = gen_vehicles(30)
    packaging_types = gen_packaging_types()
    orders = gen_orders(customers, 5200)
    shipments = gen_shipments(orders, warehouses, vehicles)
    inventory = gen_inventory(warehouses, 25)
    fuel_prices = gen_fuel_prices()
    telemetry = gen_vehicle_telemetry(vehicles, 20)
    documents = gen_documents(12)

    write_json("customers", customers)
    write_json("warehouses", warehouses)
    write_json("vehicles", vehicles)
    write_json("packaging_types", packaging_types)
    write_json("orders", orders)
    write_json("shipments", shipments)
    write_json("inventory", inventory)
    write_json("fuel_prices", fuel_prices)
    write_json("vehicle_telemetry", telemetry)
    write_json("documents", documents)

    print(f"✅ Generated datasets in {DATA_DIR}")
