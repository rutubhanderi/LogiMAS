import requests
import random
import time
from datetime import datetime, timezone
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json

# --- Configuration ---
# Load environment variables from the root .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
TELEMETRY_ENDPOINT = f"{SUPABASE_URL}/api/v1/telemetry" # Use Supabase URL since Next.js server might not be public

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in the .env file.")

# Initialize Supabase client to get vehicle IDs
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Simulator Logic ---

def get_vehicle_ids():
    """Fetch all vehicle IDs from the database."""
    print("Fetching vehicle IDs from Supabase...")
    response = supabase.from_('vehicles').select('vehicle_id').execute()
    if response.data:
        ids = [item['vehicle_id'] for item in response.data]
        print(f"Found {len(ids)} vehicles.")
        return ids
    return []

def generate_telemetry_event(vehicle_id: str):
    """Generate a single fake telemetry event."""
    return {
        "vehicle_id": vehicle_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "lat": round(random.uniform(34.0, 34.2), 6),
        "lon": round(random.uniform(-118.6, -118.3), 6),
        "speed_kmph": round(random.uniform(0, 100), 2),
        "fuel_pct": round(random.uniform(5, 95), 2),
        "cargo_temp": round(random.uniform(-5, 5), 2),
    }

def run_simulator(vehicle_ids: list, interval_seconds: int = 10):
    """Main loop to send telemetry data periodically."""
    if not vehicle_ids:
        print("No vehicle IDs found. Exiting simulator.")
        return

    print(f"Starting telemetry simulator. Sending data every {interval_seconds} seconds...")
    print(f"Target endpoint: {TELEMETRY_ENDPOINT}")
    
    while True:
        try:
            # Select a random subset of vehicles to send updates
            num_updates = random.randint(1, len(vehicle_ids) // 2)
            selected_ids = random.sample(vehicle_ids, num_updates)
            
            events_batch = [generate_telemetry_event(vid) for vid in selected_ids]
            
            print(f"\nSending batch of {len(events_batch)} events at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            response = requests.post(
                TELEMETRY_ENDPOINT, 
                headers={"Content-Type": "application/json"},
                data=json.dumps(events_batch)
            )
            
            if response.status_code == 201:
                print(f"✅ Successfully ingested batch. Response: {response.json()['message']}")
            else:
                print(f"❌ Error sending batch. Status: {response.status_code}, Response: {response.text}")

        except Exception as e:
            print(f"An error occurred in the simulator loop: {e}")
        
        time.sleep(interval_seconds)

if __name__ == "__main__":
    # The Next.js API route is a "serverless function" on Vercel.
    # To test locally, your Next.js server on localhost:3000 must be running.
    # We'll construct the local URL for the endpoint.
    LOCAL_ENDPOINT = "http://localhost:3000/api/v1/telemetry"
    print(f"Note: For local testing, ensure your Next.js server is running.")
    user_choice = input(f"Send telemetry to local endpoint ({LOCAL_ENDPOINT})? (y/n): ").lower()
    
    if user_choice == 'y':
        TELEMETRY_ENDPOINT = LOCAL_ENDPOINT
    else:
        print("Simulator will not run. Exiting.")
        exit()

    vehicle_ids = get_vehicle_ids()
    run_simulator(vehicle_ids)