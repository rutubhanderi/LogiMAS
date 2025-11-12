# src/schemas/inventory.py

from pydantic import BaseModel, Field
from uuid import UUID

class InventoryItemPublicSchema(BaseModel):
    sku: str
    product_name: str
    # We add a placeholder for price; in a real app, this might come from a different table.
    price: float = Field(default=10.0, description="Default price, adjust as needed")

    class Config:
        from_attributes = True