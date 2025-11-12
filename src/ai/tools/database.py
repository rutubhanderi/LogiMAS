import os
import traceback
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import BaseModel, Field
from langchain.tools import tool
from ...config import (
    settings,
)

SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Tool: Shipment Status Lookup ---
class ShipmentLookupSchema(BaseModel):
    """Input schema for the shipment lookup tool."""
    shipment_id: str = Field(description="The UUID of the shipment to look up.")


@tool("shipment-status-lookup", args_schema=ShipmentLookupSchema)
def get_shipment_status(shipment_id: str) -> dict:
    """Looks up the status and current ETA of a specific shipment by its ID."""
    print(f"--- Tool Executing: get_shipment_status for ID: {shipment_id} ---")
    try:
        response = (
            supabase_client.from_("shipments")
            .select("status, current_eta, vehicle_id") # Also select vehicle_id
            .eq("shipment_id", shipment_id)
            .single()
            .execute()
        )
        if response.data:
            return response.data
        else:
            return {"error": "Shipment not found."}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


# --- Tool: Inventory Level Lookup ---
class InventoryLookupSchema(BaseModel):
    """Input schema for the inventory lookup tool."""
    sku: str = Field(description="The SKU (Stock Keeping Unit) of the product to look up.")


@tool("inventory-level-lookup", args_schema=InventoryLookupSchema)
def get_inventory_level(sku: str) -> dict:
    """Looks up the quantity on hand for a specific product SKU across all warehouses."""
    print(f"--- Tool Executing: get_inventory_level for SKU: {sku} ---")
    # (Implementation remains the same)
    try:
        response = (
            supabase_client.from_("inventory")
            .select("warehouse_id, qty_on_hand")
            .eq("sku", sku)
            .execute()
        )
        if response.data:
            total_qty = sum(item["qty_on_hand"] for item in response.data)
            per_warehouse = {item["warehouse_id"]: item["qty_on_hand"] for item in response.data}
            return {
                "sku": sku,
                "total_quantity_on_hand": total_qty,
                "stock_by_warehouse": per_warehouse,
            }
        else:
            return {"error": f"SKU '{sku}' not found in inventory."}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


# --- Tool: Packaging Optimizer ---
class PackagingOptimizerSchema(BaseModel):
    """Input schema for the packaging optimizer tool."""
    item_volumes: list[float] = Field(description="A list of the individual volumes (in cm³) of each item to be packed.")


@tool("packaging-optimizer", args_schema=PackagingOptimizerSchema)
def find_best_packaging(item_volumes: list[float]) -> dict:
    """Calculates the total volume from a list of item volumes and finds the smallest box that can fit them."""
    print(f"--- Tool Executing: find_best_packaging for volumes: {item_volumes} ---")
    # (Implementation remains the same)
    try:
        if not item_volumes:
            return {"error": "No item volumes provided."}
        total_items_volume = sum(item_volumes)
        if total_items_volume <= 0:
            return {"error": "Total volume must be positive."}
        response = (
            supabase_client.from_("packaging_types")
            .select("packaging_id, name, volume_cm3, cost_per_unit")
            .gte("volume_cm3", total_items_volume)
            .order("volume_cm3", desc=False)
            .limit(1)
            .execute()
        )
        if response.data:
            best_box = response.data[0]
            wasted_space = best_box["volume_cm3"] - total_items_volume
            result = {
                "recommendation": {"box_name": best_box["name"], "box_volume_cm3": best_box["volume_cm3"]},
                "analysis": {
                    "total_items_volume_cm3": total_items_volume,
                    "wasted_space_cm3": wasted_space,
                    "efficiency_percentage": round((total_items_volume / best_box["volume_cm3"]) * 100, 2),
                },
            }
            return result
        else:
            return {"error": "No suitable packaging found. Items may be too large."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


# --- Tool: Cost Calculation ---
class CostCalculationSchema(BaseModel):
    """Input schema for the route cost calculation tool."""
    shipment_id: str = Field(description="The UUID of the shipment for which to calculate the fuel cost.")


@tool("route-fuel-cost-calculator", args_schema=CostCalculationSchema)
def calculate_route_fuel_cost(shipment_id: str) -> dict:
    """Calculates the total estimated fuel cost for a given shipment ID."""
    print(f"--- Tool Executing: calculate_route_fuel_cost for Shipment: {shipment_id} ---")
    # (Implementation remains the same)
    try:
        shipment_info_resp = (
            supabase_client.from_("shipments")
            .select("distance_km, vehicles(fuel_type, consumption_l_per_100km)")
            .eq("shipment_id", shipment_id)
            .single()
            .execute()
        )
        if not shipment_info_resp.data:
            return {"error": f"Shipment ID {shipment_id} not found."}
        shipment_info = shipment_info_resp.data
        distance = shipment_info["distance_km"]
        vehicle = shipment_info["vehicles"]
        if not vehicle:
            return {"error": "No vehicle assigned to this shipment."}
        fuel_type = vehicle["fuel_type"]
        consumption = vehicle["consumption_l_per_100km"]
        fuel_price_resp = (
            supabase_client.from_("fuel_prices")
            .select("cost_per_liter")
            .eq("fuel_type", fuel_type)
            .single()
            .execute()
        )
        if not fuel_price_resp.data:
            return {"error": f"Fuel price for '{fuel_type}' not found."}
        cost_per_unit = fuel_price_resp.data["cost_per_liter"]
        if fuel_type != "Electric":
            total_fuel_liters = (distance / 100) * consumption
            total_cost = total_fuel_liters * cost_per_unit
            unit_name = "liters"
        else:
            total_fuel_liters = distance * consumption
            total_cost = total_fuel_liters * cost_per_unit
            unit_name = "kWh"
        result = {
            "shipment_id": shipment_id,
            "distance_km": distance,
            "fuel_type": fuel_type,
            f"total_fuel_{unit_name}": round(total_fuel_liters, 2),
            "estimated_fuel_cost": f"${round(total_cost, 2)}",
        }
        return result
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


# --- NEW Tool: Order Details Lookup ---
class OrderLookupSchema(BaseModel):
    """Input schema for the order lookup tool."""
    order_id: str = Field(description="The UUID of the order to look up.")

@tool("order-details-lookup", args_schema=OrderLookupSchema)
def get_order_details(order_id: str) -> dict:
    """Looks up the details of a specific order, including items, destination, and status."""
    print(f"--- Tool Executing: get_order_details for Order ID: {order_id} ---")
    try:
        response = (
            supabase_client.from_("orders")
            .select("order_id, status, items, destination, estimated_delivery_date")
            .eq("order_id", order_id)
            .single()
            .execute()
        )
        if response.data:
            return response.data
        else:
            return {"error": "Order not found."}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


# --- NEW Tool: Vehicle Location Lookup ---
class VehicleLocationSchema(BaseModel):
    """Input schema for the vehicle location tool."""
    vehicle_id: str = Field(description="The UUID of the vehicle to locate.")

@tool("vehicle-location-lookup", args_schema=VehicleLocationSchema)
def get_vehicle_location(vehicle_id: str) -> dict:
    """Finds the most recent telemetry data (location and speed) for a specific vehicle."""
    print(f"--- Tool Executing: get_vehicle_location for Vehicle ID: {vehicle_id} ---")
    try:
        response = (
            supabase_client.from_("vehicle_telemetry")
            .select("lat, lon, speed_kmph, ts")
            .eq("vehicle_id", vehicle_id)
            .order("ts", desc=True)
            .limit(1)
            .single()
            .execute()
        )
        if response.data:
            return response.data
        else:
            return {"error": "No telemetry data found for this vehicle."}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

# --- Utility Function for Audit Logging (NOT a tool for the LLM) ---
def log_agent_decision(agent_name: str, query: str, decision: dict | str):
    """Logs the final output of an agent to the 'agent_audit_logs' table in Supabase."""
    print(f"--- Logging decision for agent: {agent_name} ---")
    try:
        decision_json = (
            json.dumps(decision)
            if isinstance(decision, dict)
            else json.dumps({"output": decision})
        )
        log_entry = {
            "agent_name": agent_name,
            "input_context": {"query": query},
            "decision_json": json.loads(decision_json),
            "confidence": 0.95,  # Placeholder
        }
        response = supabase_client.from_("agent_audit_logs").insert(log_entry).execute()
        if response.data:
            print(f"--- Successfully logged decision for {agent_name} ---")
        else:
            print(
                f"!!! WARNING: Failed to log decision for {agent_name}. Response: {response.error or 'No data returned'}"
            )
    except Exception as e:
        print(f"!!! CRITICAL WARNING: An exception occurred during audit logging: {e}")
        print(traceback.format_exc())
