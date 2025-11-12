from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum
from .order import OrderItemSchema
# --- EXISTING SCHEMAS (Unchanged) ---
class ShipmentCreateSchema(BaseModel):
    order_id: UUID = Field(..., description="The ID of the existing order to create a shipment for.")

class ShipmentPublicSchema(BaseModel):
    shipment_id: UUID
    order_id: UUID
    origin_warehouse_id: UUID
    vehicle_id: UUID
    status: str
    shipped_at: datetime
    class Config:
        from_attributes = True

# --- NEW SCHEMAS FOR THE "MY DELIVERIES" ENDPOINT ---

# A nested schema to represent basic customer info
class CustomerInfoForShipment(BaseModel):
    name: str
    phone: Optional[str] = None # <-- ADD THIS LINE
    class Config:
        from_attributes = True

class DestinationForShipment(BaseModel):
    address: str
    city: str
    class Config:
        from_attributes = True

# --- MODIFIED: Add 'items' to the order info ---
class OrderInfoForShipment(BaseModel):
    customer: CustomerInfoForShipment
    destination: DestinationForShipment
    items: List[OrderItemSchema] = [] # <-- ADD THIS LINE
    class Config:
        from_attributes = True

# The main response schema is now richer
class DriverShipmentDetailSchema(BaseModel):
    shipment_id: UUID
    status: str
    current_eta: Optional[datetime] = None
    order: OrderInfoForShipment
    # We also need the distance_km for the UI
    distance_km: Optional[float] = None # <-- ADD THIS LINE
    class Config:
        from_attributes = True

class ShipmentStatusEnum(str, Enum):
    delivered = "delivered"
    # In the future, you could add other statuses like 'delivery_failed'

# This is the Pydantic model for the request body of our new PATCH endpoint.
class ShipmentStatusUpdate(BaseModel):
    status: ShipmentStatusEnum