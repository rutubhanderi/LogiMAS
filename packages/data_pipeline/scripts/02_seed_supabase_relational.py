import os
import pandas as pd
import numpy as np  # <--- THIS IS THE NEW LINE TO FIX THE ERROR
from supabase import create_client, Client
from dotenv import load_dotenv
import json

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in the .env file.")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "generated")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase client initialized.")


def upload_csv_to_table(file_name, table_name, json_columns=None):
    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} not found. Skipping table {table_name}.")
        return True  # Return True to not halt the process

    print(f"\n--- Uploading {file_name} to '{table_name}' table ---")
    df = pd.read_csv(file_path)

    # Replace numpy.nan and pandas NA with None for JSON compatibility
    df = df.replace({pd.NA: None, np.nan: None})

    if json_columns:
        for col in json_columns:
            if col in df.columns:
                df[col] = df[col].apply(
                    lambda x: json.loads(x) if isinstance(x, str) else x
                )

    records = df.to_dict(orient="records")
    batch_size = 500
    total_records = len(records)

    for i in range(0, total_records, batch_size):
        batch = records[i : i + batch_size]
        try:
            print(
                f"Uploading records {i+1} to {min(i+batch_size, total_records)} of {total_records}..."
            )
            response = supabase.table(table_name).insert(batch).execute()

            # Check for API errors in the response
            if hasattr(response, "error") and response.error:
                raise Exception(f"API Error: {response.error.message}")

        except Exception as e:
            print(f"!!!!!!!! AN ERROR OCCURRED !!!!!!!!")
            print(
                f"Error while inserting into '{table_name}' (batch starting at record {i+1}):"
            )
            print(str(e))
            print("Aborting script.")
            return False  # Indicate failure

    print(f"Successfully uploaded {total_records} records to '{table_name}'.")
    return True  # Indicate success


def main():
    print("Starting database seeding process...")

    # The order is important to respect foreign key constraints.
    if not upload_csv_to_table("warehouses.csv", "warehouses"):
        return
    if not upload_csv_to_table("customers.csv", "customers", json_columns=["address"]):
        return
    if not upload_csv_to_table("vehicles.csv", "vehicles"):
        return
    if not upload_csv_to_table(
        "orders.csv", "orders", json_columns=["items", "destination"]
    ):
        return
    if not upload_csv_to_table("shipments.csv", "shipments"):
        return

    print("\nDatabase seeding process completed successfully!")


if __name__ == "__main__":
    main()
