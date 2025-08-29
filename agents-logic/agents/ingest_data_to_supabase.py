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
            # Optional: break or log the failing chunk
            # with open(f"failed_{table_name}_{i}.json", "w") as f:
            #     json.dump(chunk, f)

def ingest_data_to_supabase():
    print("--- Ingesting structured data into Supabase ---")
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file.")
        return

    supabase: Client = create_client(url, key)
    
    for csv_file, table_name in CSV_TO_TABLE_MAP.items():
        print(f"\nProcessing {csv_file} for table '{table_name}'...")
        try:
            df = pd.read_csv(csv_file)
            # Replace NaN with None for JSON compatibility
            df = df.where(pd.notnull(df), None)
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