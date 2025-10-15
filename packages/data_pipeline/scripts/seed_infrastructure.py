import os
import random
import pandas as pd
from faker import Faker
from supabase import create_client, Client
from dotenv import load_dotenv

# --- CONFIGURATION ---
# Adjust these numbers to control how much data is generated
NUM_WAREHOUSES = 20
NUM_VEHICLES = 50

# --- INITIALIZATION ---
# Assumes your .env file is three directories above the script's location
# Modify this path if your folder structure is different
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in your .env file.")

fake = Faker()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase admin client initialized.")


def generate_warehouses(count: int) -> pd.DataFrame:
    """Generates synthetic data for warehouses."""
    print(f"--- Generating {count} warehouses... ---")
    warehouses_data = [
        {
            "warehouse_id": fake.uuid4(),
            "name": f"{fake.city()} Distribution Center",
            "lat": float(fake.latitude()),
            "lon": float(fake.longitude()),
            "region": random.choice(["North America", "Europe", "Asia-Pacific", "South America", "Africa"]),
        }
        for _ in range(count)
    ]
    return pd.DataFrame(warehouses_data)


def generate_vehicles(count: int) -> pd.DataFrame:
    """Generates synthetic data for vehicles."""
    print(f"--- Generating {count} vehicles... ---")
    vehicles_data = []
    vehicle_types = {
        "Cargo Van": {"capacity_kg": 2000, "capacity_volume_cm3": 12_000_000},
        "Refrigerated Truck": {"capacity_kg": 7000, "capacity_volume_cm3": 40_000_000},
        "Box Truck": {"capacity_kg": 5000, "capacity_volume_cm3": 35_000_000},
        "Flatbed Truck": {"capacity_kg": 20000, "capacity_volume_cm3": 60_000_000},
    }

    for _ in range(count):
        v_type = random.choice(list(vehicle_types.keys()))
        vehicles_data.append(
            {
                "vehicle_id": fake.uuid4(),
                "vehicle_type": v_type,
                "capacity_kg": vehicle_types[v_type]["capacity_kg"] * random.uniform(0.9, 1.1),
                "capacity_volume_cm3": vehicle_types[v_type]["capacity_volume_cm3"] * random.uniform(0.9, 1.1),
                "fuel_type": random.choice(["Diesel", "Gasoline", "Electric"]),
                "status": random.choices(["Available", "In-Transit", "Maintenance"], weights=[0.8, 0.15, 0.05])[0],
            }
        )
    return pd.DataFrame(vehicles_data)


def upload_dataframe(df: pd.DataFrame, table_name: str):
    """Uploads a pandas DataFrame to a Supabase table."""
    if df.empty:
        print(f"DataFrame for '{table_name}' is empty. Skipping upload.")
        return

    print(f"--- Uploading {len(df)} records to '{table_name}' table ---")
    records = df.to_dict(orient="records")
    
    try:
        response = supabase.table(table_name).insert(records).execute()
    except Exception as e:
        print(f"!!! An exception occurred uploading to '{table_name}': {e}")
        return
        
    print(f"Successfully uploaded data to '{table_name}'.")


def main():
    """Main function to clear and seed the infrastructure tables."""
    if (
        input(
            "This script will DELETE and re-seed warehouses, vehicles, inventory, and shipments. Are you sure? (y/n): "
        ).lower()
        != "y"
    ):
        print("Aborting.")
        return

    print("--- Clearing existing data... ---")
    # Delete from tables in the correct order to respect foreign key constraints
    # Any table with a FK to warehouses or vehicles must be cleared first.
    supabase.from_("shipments").delete().neq("shipment_id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.from_("inventory").delete().neq("inventory_id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.from_("warehouses").delete().neq("warehouse_id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.from_("vehicles").delete().neq("vehicle_id", "00000000-0000-0000-0000-000000000000").execute()
    print("--- Dependent and target data cleared. ---")

    # Generate and upload new data
    warehouses_df = generate_warehouses(NUM_WAREHOUSES)
    vehicles_df = generate_vehicles(NUM_VEHICLES)

    upload_dataframe(warehouses_df, "warehouses")
    upload_dataframe(vehicles_df, "vehicles")

    print("\n✅ Infrastructure data (warehouses and vehicles) seeding complete!")


if __name__ == "__main__":
    main()