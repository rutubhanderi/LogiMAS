import os
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

# --- Tool Definition ---

class ShipmentLookupSchema(BaseModel):
    """Input schema for the shipment lookup tool."""
    shipment_id: str = Field(description="The UUID of the shipment to look up.")

@tool("shipment-status-lookup", args_schema=ShipmentLookupSchema)
def get_shipment_status(shipment_id: str) -> dict:
    """
    Looks up the status and current ETA of a specific shipment by its ID.
    Returns a dictionary with the shipment's status and ETA.
    """
    print(f"--- Tool Executing: get_shipment_status for ID: {shipment_id} ---")
    try:
        response = supabase_client.from_('shipments') \
            .select('status, current_eta') \
            .eq('shipment_id', shipment_id) \
            .single() \
            .execute()
        
        if response.data:
            return response.data
        else:
            return {"error": "Shipment not found."}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

class InventoryLookupSchema(BaseModel):
    """Input schema for the inventory lookup tool."""
    sku: str = Field(description="The SKU (Stock Keeping Unit) of the product to look up.")

@tool("inventory-level-lookup", args_schema=InventoryLookupSchema)
def get_inventory_level(sku: str) -> dict:
    """
    Looks up the quantity on hand for a specific product SKU across all warehouses.
    Returns a dictionary with the total quantity and stock levels per warehouse.
    """
    print(f"--- Tool Executing: get_inventory_level for SKU: {sku} ---")
    try:
        response = supabase_client.from_('inventory') \
            .select('warehouse_id, qty_on_hand') \
            .eq('sku', sku) \
            .execute()
        
        if response.data:
            total_qty = sum(item['qty_on_hand'] for item in response.data)
            per_warehouse = {item['warehouse_id']: item['qty_on_hand'] for item in response.data}
            return {
                "sku": sku,
                "total_quantity_on_hand": total_qty,
                "stock_by_warehouse": per_warehouse
            }
        else:
            return {"error": f"SKU '{sku}' not found in inventory."}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}