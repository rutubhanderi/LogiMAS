import os
import random
from datetime import datetime, timedelta, timezone
import pandas as pd
from faker import Faker
from supabase import create_client, Client
from dotenv import load_dotenv

# --- CONFIGURATION ---
# How many data points to generate for each vehicle
POINTS_PER_VEHICLE = 250
# The time window for the telemetry data (e.g., generate data for the last 30 days)
TIME_SPAN_DAYS = 30

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


def generate_telemetry_data() -> pd.DataFrame:
    """Generates synthetic time-series telemetry data for existing vehicles."""
    print("--- Generating vehicle telemetry data... ---")

    try:
        # Fetch all vehicle IDs to create telemetry for
        vehicles = supabase.from_("vehicles").select("vehicle_id, vehicle_type").execute().data
        if not vehicles:
            print("!!! WARNING: No vehicles found in the database. Cannot generate telemetry.")
            return pd.DataFrame()
    except Exception as e:
        print(f"!!! Error fetching vehicles: {e}")
        return pd.DataFrame()

    telemetry_data = []
    start_time_window = datetime.now(timezone.utc) - timedelta(days=TIME_SPAN_DAYS)

    for vehicle in vehicles:
        vehicle_id = vehicle["vehicle_id"]
        vehicle_type = vehicle["vehicle_type"]

        # --- Simulate a single journey for each vehicle ---
        # Start the journey at a random time within our window
        current_ts = start_time_window + timedelta(seconds=random.randint(0, TIME_SPAN_DAYS * 24 * 3600))
        current_lat = float(fake.latitude())
        current_lon = float(fake.longitude())
        
        # Start with a full tank and a random initial speed
        current_fuel_pct = 100.0
        current_speed = random.uniform(40, 90) # Start at a cruising speed

        for i in range(POINTS_PER_VEHICLE):
            # Move the timestamp forward by 5 to 15 minutes
            current_ts += timedelta(minutes=random.randint(5, 15))
            
            # Slightly adjust speed (e.g., traffic, stops)
            speed_change = random.uniform(-15, 15)
            current_speed = max(0, min(120, current_speed + speed_change)) # Keep speed between 0 and 120

            # Drain fuel based on speed; more speed = more fuel used
            fuel_drain = (current_speed / 100) * random.uniform(0.3, 0.6)
            current_fuel_pct = max(0, current_fuel_pct - fuel_drain)

            # If fuel is out, stop the vehicle
            if current_fuel_pct == 0:
                current_speed = 0

            # Simulate location change based on speed and time passed
            # This is a simple approximation, not a true physics model
            lat_change = (current_speed / 10000) * random.uniform(-1, 1)
            lon_change = (current_speed / 10000) * random.uniform(-1, 1)
            current_lat += lat_change
            current_lon += lon_change

            # Simulate cargo temperature based on vehicle type
            if "Refrigerated" in vehicle_type:
                cargo_temp = random.uniform(2, 5) # Chilled
            else:
                cargo_temp = random.uniform(18, 25) # Ambient

            telemetry_data.append({
                "vehicle_id": vehicle_id,
                "ts": current_ts.isoformat(),
                "lat": current_lat,
                "lon": current_lon,
                "speed_kmph": round(current_speed, 2),
                "fuel_pct": round(current_fuel_pct, 2),
                "cargo_temp": round(cargo_temp, 2),
            })
            
    print(f"Generated {len(telemetry_data)} telemetry points for {len(vehicles)} vehicles.")
    return pd.DataFrame(telemetry_data)


def upload_dataframe(df: pd.DataFrame, table_name: str):
    """Uploads a pandas DataFrame to a Supabase table in batches."""
    if df.empty:
        print(f"DataFrame for '{table_name}' is empty. Skipping upload.")
        return

    print(f"--- Uploading data to '{table_name}' table ---")
    records = df.to_dict(orient="records")
    
    # Batch inserts to avoid payload size limits
    for i in range(0, len(records), 500):
        batch = records[i : i + 500]
        try:
            supabase.table(table_name).insert(batch).execute()
        except Exception as e:
            print(f"!!! An exception occurred uploading to '{table_name}': {e}")
            return
            
    print(f"Successfully uploaded {len(records)} records to '{table_name}'.")


def main():
    """Main function to clear and seed the vehicle_telemetry table."""
    if (
        input(
            "This script will DELETE and re-seed all vehicle telemetry. Are you sure? (y/n): "
        ).lower()
        != "y"
    ):
        print("Aborting.")
        return

    print("--- Clearing existing telemetry data... ---")
    supabase.from_("vehicle_telemetry").delete().neq("id", 0).execute()
    print("--- Telemetry data cleared. ---")

    telemetry_df = generate_telemetry_data()
    upload_dataframe(telemetry_df, "vehicle_telemetry")

    print("\n✅ Vehicle telemetry seeding complete!")


if __name__ == "__main__":
    main()