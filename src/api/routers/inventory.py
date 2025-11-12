# src/api/routers/inventory.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ... import database, security
from ...schemas import inventory as inventory_schema
from ...services import inventory_service

router = APIRouter()

@router.get(
    "/skus",
    response_model=List[inventory_schema.InventoryItemPublicSchema],
    summary="Get all available inventory SKUs",
    description="Returns a list of all unique products in inventory for order placement."
)
def get_inventory_skus(
    db: Session = Depends(database.get_db),
    # Protect the endpoint to ensure only logged-in users can see inventory
    current_user: dict = Depends(security.get_current_active_user)
):
    try:
        items = inventory_service.get_all_inventory_items(db)
        # Manually adding a price for demonstration purposes
        # A real application would likely have a price on the product/inventory table
        response_items = []
        for item in items:
            item_data = inventory_schema.InventoryItemPublicSchema.from_orm(item)
            # Example pricing logic: set a default or calculate
            item_data.price = 15.75 if "PROD" in item.sku else 25.50
            response_items.append(item_data)
        return response_items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch inventory items: {str(e)}"
        )