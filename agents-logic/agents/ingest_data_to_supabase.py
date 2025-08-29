import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# --- Configuration ---
# The order is important to respect foreign key constraints
CSV_TO_TABLE_MAP = {
    'locations_india.csv': 'locations',
    'warehouses.csv': 'warehouses',
    'products.csv': 'products',
    'stock_levels.csv': 'stock_levels',
    'sales_history.csv': 'sales_history',
    'transport_routes.csv': 'transport_routes',
    'restock_deliveries.csv': 'restock_deliveries'
}

def insert_in_chunks(supabase_client: Client, table_name: str, records: list, chunk_size: int = 500):
    """Inserts records into a Supabase table in manageable chunks."""
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        try:
            supabase_client.table(table_name).insert(chunk).execute()
            print(f"  Inserted chunk {i // chunk_size + 1} into '{table_name}' ({len(chunk)} records)")
        except Exception as e:
            print(f"  ❌ Error inserting chunk into '{table_name}': {e}")

def ingest_data_to_supabase():
    print("--- Ingesting structured data into Supabase ---")

    # --- FIX: Always load .env from project root ---
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file.")
        return

    supabase: Client = create_client(url, key)

    for csv_file, table_name in CSV_TO_TABLE_MAP.items():
        print(f"\nProcessing {csv_file} for table '{table_name}'...")
        try:
            df = pd.read_csv(os.path.join(BASE_DIR, "data", csv_file))
            df = df.where(pd.notnull(df), None)  # Replace NaN with None
            records = df.to_dict(orient='records')

            if records:
                insert_in_chunks(supabase, table_name, records)
                print(f"✅ Successfully finished ingestion for '{table_name}'.")
            else:
                print(f"  No records found in {csv_file}. Skipping.")

        except FileNotFoundError:
            print(f"⚠️ Warning: {csv_file} not found. Skipping.")
        except Exception as e:
            print(f"❌ An unexpected error occurred with {csv_file}: {e}")

    print("\n--- Supabase Ingestion Complete ---")

if __name__ == "__main__":
    ingest_data_to_supabase()
