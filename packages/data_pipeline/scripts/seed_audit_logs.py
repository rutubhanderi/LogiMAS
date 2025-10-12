"""
Seed Agent Audit Logs
Populates sample agent decision logs for demonstration
"""

import os
import json
from datetime import datetime, timedelta, timezone
import random
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in .env file")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sample agent decisions
AGENT_DECISIONS = [
    {
        "agent_name": "routing_agent",
        "decision": "Optimized route for 15 deliveries in downtown area",
        "confidence": 0.92,
        "input_context": {
            "num_deliveries": 15,
            "area": "downtown",
            "traffic_level": "moderate",
            "time_window": "9AM-5PM"
        }
    },
    {
        "agent_name": "delay_prediction_agent",
        "decision": "Predicted 45-minute delay due to traffic congestion",
        "confidence": 0.87,
        "input_context": {
            "shipment_id": "SHP-12345",
            "current_location": "Highway 101",
            "destination": "San Francisco",
            "traffic_data": "heavy congestion reported"
        }
    },
    {
        "agent_name": "customer_service_agent",
        "decision": "Recommended expedited shipping for time-sensitive package",
        "confidence": 0.95,
        "input_context": {
            "customer_query": "Need urgent delivery by tomorrow",
            "package_weight": "5 lbs",
            "destination": "Los Angeles"
        }
    },
    {
        "agent_name": "inventory_agent",
        "decision": "Suggested restocking warehouse with high-demand items",
        "confidence": 0.89,
        "input_context": {
            "warehouse_id": "WH-001",
            "low_stock_items": ["boxes_large", "bubble_wrap"],
            "demand_trend": "increasing"
        }
    },
    {
        "agent_name": "routing_agent",
        "decision": "Rerouted delivery due to road closure",
        "confidence": 0.91,
        "input_context": {
            "original_route": "Highway 5",
            "closure_reason": "construction",
            "alternative_route": "Highway 99",
            "additional_time": "20 minutes"
        }
    },
    {
        "agent_name": "quality_check_agent",
        "decision": "Flagged package for inspection due to weight discrepancy",
        "confidence": 0.88,
        "input_context": {
            "expected_weight": "10 lbs",
            "actual_weight": "12 lbs",
            "package_id": "PKG-67890"
        }
    },
    {
        "agent_name": "customer_service_agent",
        "decision": "Provided tracking information and estimated delivery time",
        "confidence": 0.96,
        "input_context": {
            "customer_query": "Where is my package?",
            "shipment_id": "SHP-54321",
            "current_status": "in_transit"
        }
    },
    {
        "agent_name": "capacity_planning_agent",
        "decision": "Recommended adding extra vehicle for peak season",
        "confidence": 0.85,
        "input_context": {
            "current_capacity": "85%",
            "projected_demand": "120%",
            "season": "holiday"
        }
    },
    {
        "agent_name": "delay_prediction_agent",
        "decision": "No delays expected, on-time delivery confirmed",
        "confidence": 0.93,
        "input_context": {
            "shipment_id": "SHP-11111",
            "weather": "clear",
            "traffic": "light",
            "vehicle_status": "optimal"
        }
    },
    {
        "agent_name": "incident_response_agent",
        "decision": "Dispatched replacement vehicle for breakdown",
        "confidence": 0.90,
        "input_context": {
            "incident_type": "vehicle_breakdown",
            "location": "Interstate 10",
            "affected_shipments": 8,
            "response_time": "30 minutes"
        }
    },
]

def seed_audit_logs():
    """Create sample audit logs"""
    print(f"\n--- Seeding {len(AGENT_DECISIONS) * 5} Agent Audit Logs ---")
    
    logs_to_insert = []
    start_time = datetime.now(timezone.utc) - timedelta(days=30)
    
    # Create multiple logs over the past 30 days
    for _ in range(5):  # Create 5 logs for each decision type
        for decision in AGENT_DECISIONS:
            # Random timestamp within the last 30 days
            random_offset = random.randint(0, 30 * 24 * 60 * 60)
            timestamp = start_time + timedelta(seconds=random_offset)
            
            log_entry = {
                "agent_name": decision["agent_name"],
                "decision_json": {
                    "decision": decision["decision"],
                    "timestamp": timestamp.isoformat(),
                    "metadata": decision["input_context"]
                },
                "confidence": decision["confidence"] + random.uniform(-0.05, 0.05),  # Add slight variation
                "timestamp": timestamp.isoformat(),
                "input_context": decision["input_context"]
            }
            
            logs_to_insert.append(log_entry)
    
    # Insert in batches
    batch_size = 100
    total_inserted = 0
    
    for i in range(0, len(logs_to_insert), batch_size):
        batch = logs_to_insert[i:i + batch_size]
        try:
            response = supabase.table("agent_audit_logs").insert(batch).execute()
            total_inserted += len(batch)
            print(f"✓ Inserted batch {i//batch_size + 1}: {len(batch)} logs")
        except Exception as e:
            print(f"❌ Error inserting batch: {str(e)}")
    
    print(f"✓ Successfully inserted {total_inserted} audit logs")
    return True

def main():
    print("="*60)
    print("AGENT AUDIT LOGS SEEDING")
    print("="*60)
    
    # Clear existing logs (optional)
    try:
        print("\n--- Clearing existing audit logs ---")
        supabase.table("agent_audit_logs").delete().neq("log_id", 0).execute()
        print("✓ Cleared existing logs")
    except Exception as e:
        print(f"⚠ Warning: {str(e)}")
    
    # Seed logs
    success = seed_audit_logs()
    
    if success:
        print("\n" + "="*60)
        print("✓ AUDIT LOGS SEEDING COMPLETE!")
        print("="*60)
    else:
        print("\n❌ Seeding failed")

if __name__ == "__main__":
    main()
