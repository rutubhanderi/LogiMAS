from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# Defines a single item within an order
class OrderItemSchema(BaseModel):
    sku: str
    name: str
    qty: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

# Defines the destination address
class DestinationSchema(BaseModel):
    address: str
    city: str
    postal_code: str
    lat: Optional[float] = None
    lon: Optional[float] = None

# The main schema for the incoming request from the frontend
class OrderCreateSchema(BaseModel):
    items: List[OrderItemSchema] = Field(..., min_items=1)
    destination: DestinationSchema

# The public representation of a created order (this will be our response model)
class OrderPublicSchema(BaseModel):
    order_id: UUID
    customer_id: UUID
    order_date: datetime
    order_total: float
    status: str
    items: List[OrderItemSchema]
    destination: DestinationSchema

    class Config:
        from_attributes = True
