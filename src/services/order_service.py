import math
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from .. import models
from ..schemas import order as order_schema

def get_coords_from_address(address: str, city: str, postal_code: str):
    """Converts a physical address into latitude and longitude."""
    try:
        geolocator = Nominatim(user_agent="logimas_app")
        full_address = f"{address}, {city}, {postal_code}"
        print(f"--- Geocoding address: {full_address} ---")
        location = geolocator.geocode(full_address, timeout=10)
        if location:
            print(f"--- Geocoding successful: ({location.latitude}, {location.longitude}) ---")
            return location.latitude, location.longitude
        print("--- Geocoding failed: Address not found ---")
        return None, None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"--- Geocoding service error: {e} ---")
        return None, None

# --- RENAMED & SIMPLIFIED: This function now only creates an order ---
def create_order(db: Session, order_data: order_schema.OrderCreateSchema, customer_id: UUID):
    """
    Orchestrates the creation of an order, including geocoding the destination.
    Shipment creation is no longer part of this process.
    """
    # 1. Geocode the destination address to get coordinates
    dest_lat, dest_lon = get_coords_from_address(
        order_data.destination.address,
        order_data.destination.city,
        order_data.destination.postal_code
    )
    if not dest_lat or not dest_lon:
        raise ValueError("Could not verify the destination address. Please ensure it is a valid and complete address.")
    
    # Update the destination object with the coordinates
    order_data.destination.lat = dest_lat
    order_data.destination.lon = dest_lon

    # 2. Calculate total order value
    order_total = sum(item.qty * item.price for item in order_data.items)

    # 3. Create the Order object
    db_order = models.Order(
        customer_id=customer_id,
        order_date=datetime.now(timezone.utc),
        order_total=order_total,
        items=[item.dict() for item in order_data.items],
        destination=order_data.destination.dict(),
        status="pending", # The initial status of a new order
        estimated_delivery_date=datetime.now(timezone.utc) + timedelta(days=7)
    )
    
    # 4. Add to session, commit, and refresh
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # 5. Return only the created order
    return db_order

def get_orders_by_status(db: Session, status: str):
    """
    Retrieves a list of all orders that match a given status.
    """
    return db.query(models.Order).filter(models.Order.status == status).order_by(models.Order.order_date.desc()).all()