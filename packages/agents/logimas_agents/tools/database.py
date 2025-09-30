import os
import traceback
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

# --- Supabase Client Setup ---
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in the .env file.")
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Tool: Shipment Status Lookup ---
class ShipmentLookupSchema(BaseModel):
    shipment_id: str = Field(description="The UUID of the shipment to look up.")
@tool("shipment-status-lookup", args_schema=ShipmentLookupSchema)
def get_shipment_status(shipment_id: str) -> dict:
    """Looks up the status and current ETA of a specific shipment by its ID."""
    print(f"--- Tool Executing: get_shipment_status for ID: {shipment_id} ---")
    try:
        response = supabase_client.from_('shipments').select('status, current_eta').eq('shipment_id', shipment_id).single().execute()
        if response.data: return response.data
        else: return {"error": "Shipment not found."}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

# --- Tool: Inventory Level Lookup ---
class InventoryLookupSchema(BaseModel):
    sku: str = Field(description="The SKU (Stock Keeping Unit) of the product to look up.")
@tool("inventory-level-lookup", args_schema=InventoryLookupSchema)
def get_inventory_level(sku: str) -> dict:
    """Looks up the quantity on hand for a specific product SKU across all warehouses."""
    print(f"--- Tool Executing: get_inventory_level for SKU: {sku} ---")
    try:
        response = supabase_client.from_('inventory').select('warehouse_id, qty_on_hand').eq('sku', sku).execute()
        if response.data:
            total_qty = sum(item['qty_on_hand'] for item in response.data)
            per_warehouse = {item['warehouse_id']: item['qty_on_hand'] for item in response.data}
            return {"sku": sku, "total_quantity_on_hand": total_qty, "stock_by_warehouse": per_warehouse}
        else: return {"error": f"SKU '{sku}' not found in inventory."}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

# --- Tool: Packaging Optimizer (ROBUST ALTERNATIVE) ---
class PackagingOptimizerSchema(BaseModel):
    item_volumes: list[float] = Field(description="A list of the individual volumes (in cm³) of each item to be packed. For example [250.0, 200.0].")

@tool("packaging-optimizer", args_schema=PackagingOptimizerSchema)
def find_best_packaging(item_volumes: list[float]) -> dict:
    """Calculates the total volume from a list of item volumes and finds the smallest box that can fit them."""
    print(f"--- Tool Executing (Robust): find_best_packaging for volumes: {item_volumes} ---")
    try:
        if not item_volumes: return {"error": "No item volumes provided."}
        total_items_volume = sum(item_volumes)
        if total_items_volume <= 0: return {"error": "Total volume must be positive."}

        # Step 1: Fetch ALL packaging types that are big enough.
        # We REMOVE the problematic .order() and .limit() calls.
        response = supabase_client.from_('packaging_types') \
            .select('packaging_id, name, volume_cm3, cost_per_unit') \
            .gte('volume_cm3', total_items_volume) \
            .execute()
        
        if response.data:
            # Step 2: Sort the results here in Python.
            # This is foolproof and does not depend on the library's syntax.
            suitable_boxes = sorted(response.data, key=lambda box: box['volume_cm3'])
            best_box = suitable_boxes[0] # The first one after sorting is the smallest.
            
            wasted_space = best_box['volume_cm3'] - total_items_volume
            result = {
                "recommendation": {"box_name": best_box['name'], "box_volume_cm3": best_box['volume_cm3']},
                "analysis": {"total_items_volume_cm3": total_items_volume, "wasted_space_cm3": wasted_space, "efficiency_percentage": round((total_items_volume / best_box['volume_cm3']) * 100, 2)}
            }
            print(f"--- Tool Succeeded. Returning: {result} ---")
            return result
        else:
            return {"error": "No suitable packaging found. Items may be too large."}

    except Exception as e:
        print(f"!!! TOOL FAILED: An exception occurred in find_best_packaging !!!")
        print(traceback.format_exc())
        return {"error": f"An unexpected error occurred: {str(e)}"}