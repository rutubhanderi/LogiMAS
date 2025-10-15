import os
import random
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
from faker import Faker
from supabase import create_client, Client
from dotenv import load_dotenv

# --- CONFIGURATION ---
# The number of unique products to create in the inventory.
# The total number of inventory records will be this number times the number of warehouses.
NUM_UNIQUE_PRODUCTS = 200

# --- INITIALIZATION ---
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in your .env file.")

fake = Faker()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase admin client initialized.")


def generate_static_data():
    """Generates DataFrames for relatively static lookup tables."""
    print("--- Generating static data (fuel, packaging)... ---")
    
    # 1. Fuel Prices
    fuel_data = [
        {"fuel_type": "Diesel", "cost_per_liter": round(random.uniform(1.50, 2.10), 2)},
        {"fuel_type": "Gasoline", "cost_per_liter": round(random.uniform(1.60, 2.30), 2)},
        {"fuel_type": "Electric", "cost_per_liter": round(random.uniform(0.50, 0.90), 2)}, # Using cost per kWh as a proxy
    ]
    fuel_df = pd.DataFrame(fuel_data)
    print(f"Generated {len(fuel_df)} fuel price records.")

    # 2. Packaging Types
    packaging_data = [
        {"name": "Small Padded Envelope", "length_cm": 25, "width_cm": 18, "height_cm": 1, "cost_per_unit": 0.30},
        {"name": "Large Padded Envelope", "length_cm": 45, "width_cm": 30, "height_cm": 2, "cost_per_unit": 0.55},
        {"name": "Small Box", "length_cm": 20, "width_cm": 15, "height_cm": 10, "cost_per_unit": 0.70},
        {"name": "Medium Box", "length_cm": 40, "width_cm": 30, "height_cm": 25, "cost_per_unit": 1.20},
        {"name": "Large Box", "length_cm": 60, "width_cm": 45, "height_cm": 40, "cost_per_unit": 2.50},
        {"name": "Tube", "length_cm": 90, "width_cm": 10, "height_cm": 10, "cost_per_unit": 1.80},
    ]
    # Add UUIDs for local use before upload
    for item in packaging_data:
        item['packaging_id'] = fake.uuid4()
        
    packaging_df = pd.DataFrame(packaging_data)
    print(f"Generated {len(packaging_df)} packaging types.")
    
    return fuel_df, packaging_df


def generate_inventory(count: int) -> pd.DataFrame:
    """Generates synthetic inventory data for each warehouse."""
    print("--- Generating inventory data... ---")
    
    try:
        warehouses = supabase.from_("warehouses").select("warehouse_id").execute().data
        if not warehouses:
            print("!!! WARNING: No warehouses found. Inventory cannot be generated.")
            return pd.DataFrame()
    except Exception as e:
        print(f"!!! Error fetching warehouses: {e}")
        return pd.DataFrame()

    inventory_data = []
    product_names = [f"Product {fake.word().capitalize()}" for _ in range(count)]
    
    # Create an inventory record for each product in each warehouse
    for warehouse in warehouses:
        for i in range(count):
            qty = random.randint(0, 500)
            reorder_point = random.randint(20, 50)
            inventory_data.append({
                "inventory_id": fake.uuid4(),
                "warehouse_id": warehouse["warehouse_id"],
                "sku": f"SKU-{i:04d}",
                "product_name": product_names[i],
                "qty_on_hand": qty,
                "reorder_point": reorder_point,
            })
            
    print(f"Generated {len(inventory_data)} inventory records across {len(warehouses)} warehouses.")
    return pd.DataFrame(inventory_data)


def generate_packaging_usage(packaging_df: pd.DataFrame) -> pd.DataFrame:
    """Generates synthetic packaging usage data based on existing orders."""
    print("--- Generating packaging usage data... ---")
    
    try:
        orders = supabase.from_("orders").select("order_id").execute().data
        if not orders:
            print("!!! WARNING: No orders found. Packaging usage cannot be generated.")
            return pd.DataFrame()
    except Exception as e:
        print(f"!!! Error fetching orders: {e}")
        return pd.DataFrame()

    usage_data = []
    
    # Create a usage record for each order
    for order in orders:
        # Choose a random package for this order
        package = packaging_df.sample(n=1).iloc[0]
        package_volume = package["length_cm"] * package["width_cm"] * package["height_cm"]
        
        # Simulate the volume of items, ensuring it fits in the package
        items_volume = package_volume * random.uniform(0.3, 0.8)
        wasted_space = package_volume - items_volume

        usage_data.append({
            "usage_id": fake.uuid4(),
            "order_id": order["order_id"],
            "packaging_id": package["packaging_id"],
            "items_volume_cm3": round(items_volume, 2),
            "wasted_space_cm3": round(wasted_space, 2),
        })

    print(f"Generated {len(usage_data)} packaging usage records.")
    return pd.DataFrame(usage_data)


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
        # Print a snippet of the data that failed for debugging
        print("Data snippet:", json.dumps(records[0], indent=2))
        return
        
    print(f"Successfully uploaded data to '{table_name}'.")


def main():
    """Main function to clear and seed supporting data tables."""
    if (
        input(
            "This script will DELETE and re-seed fuel prices, packaging, inventory, and packaging usage. Are you sure? (y/n): "
        ).lower()
        != "y"
    ):
        print("Aborting.")
        return

    print("--- Clearing existing data... ---")
    # Delete in reverse order of dependency
    supabase.from_("packaging_usage").delete().neq("usage_id", 0).execute()
    supabase.from_("inventory").delete().neq("inventory_id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.from_("packaging_types").delete().neq("packaging_id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.from_("fuel_prices").delete().neq("fuel_type", "none").execute()
    print("--- Data cleared. ---")

    # Generate and upload data
    fuel_df, packaging_df = generate_static_data()
    inventory_df = generate_inventory(NUM_UNIQUE_PRODUCTS)
    packaging_usage_df = generate_packaging_usage(packaging_df)

    # Upload in order of dependency
    upload_dataframe(fuel_df, "fuel_prices")
    upload_dataframe(packaging_df, "packaging_types")
    upload_dataframe(inventory_df, "inventory")
    upload_dataframe(packaging_usage_df, "packaging_usage")

    print("\n✅ Supporting data seeding complete!")


if __name__ == "__main__":
    main()