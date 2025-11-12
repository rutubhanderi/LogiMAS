# src/services/inventory_service.py

from sqlalchemy.orm import Session
from .. import models

def get_all_inventory_items(db: Session):
    """
    Retrieves all unique inventory items (SKUs) from the database.
    """
    # In a real app, you might want to join with a products table for price.
    # For now, we'll return what's in the inventory.
    return db.query(models.Inventory).distinct(models.Inventory.sku).all()