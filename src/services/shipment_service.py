import math
from uuid import UUID
from datetime import datetime, timezone,timedelta
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from .. import models

# Using your actual warehouse data
WAREHOUSES = [
    {"id": UUID("5c18fd31-8be8-4f42-92ac-85209d2f187f"), "name": "Delhi Central", "lat": 28.445837, "lon": 76.927263},
    {"id": UUID("621d784c-487d-4be2-aaf0-b8d53546728c"), "name": "Chennai Hub", "lat": 13.075915, "lon": 80.303263},
    {"id": UUID("74dc4d39-8ce3-4e86-9035-96502f35ec62"), "name": "Mumbai Hub", "lat": 18.825289, "lon": 72.783377},
    {"id": UUID("82420b14-9fe2-40d9-b93e-81b45761d4de"), "name": "Ahmedabad Central", "lat": 22.998568, "lon": 72.459022},
    {"id": UUID("bd5dd376-b2dc-4204-8c3b-f79a11c2ddee"), "name": "Bangalore Hub", "lat": 13.114791, "lon": 77.511562},
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_closest_warehouse(dest_lat: float, dest_lon: float):
    closest = None
    min_dist = float('inf')
    for wh in WAREHOUSES:
        dist = haversine(dest_lat, dest_lon, wh["lat"], wh["lon"])
        if dist < min_dist:
            min_dist = dist
            closest = wh
    return closest, min_dist

def find_available_vehicle(db: Session):
    return db.query(models.Vehicle).filter(models.Vehicle.status == 'active').first()

def create_shipment_for_order(db: Session, order_id: UUID):
    """
    Creates a shipment for an existing, pending order.
    This is a transactional operation.
    """
    # 1. Fetch the order and ensure it's valid for shipment
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    if order.status != 'pending':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Order is already '{order.status}' and cannot be shipped again.")

    # 2. Find closest warehouse and an available vehicle
    destination = order.destination
    closest_warehouse, distance_km = find_closest_warehouse(destination['lat'], destination['lon'])
    if not closest_warehouse:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Destination is outside our serviceable area.")

    vehicle = find_available_vehicle(db)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No delivery vehicles are available at the moment.")

    # 3. Create the Shipment record
    db_shipment = models.Shipment(
        order_id=order.order_id,
        origin_warehouse_id=closest_warehouse["id"],
        vehicle_id=vehicle.vehicle_id,
        shipped_at=datetime.now(timezone.utc),
        expected_arrival=datetime.now(timezone.utc) + timedelta(days=2),
        status="in-transit",
        distance_km=round(distance_km, 2)
    )
    db.add(db_shipment)

    # 4. Update the order and vehicle statuses
    order.status = 'shipped'
    vehicle.status='in-transit'
    # 5. Commit the transaction
    db.commit()
    db.refresh(db_shipment)

    return db_shipment


def get_shipments_for_driver(db: Session, driver_id: UUID):
    """
    Fetches all shipments assigned to a specific driver.
    This query joins across shipments, vehicles, orders, and customers to collect all
    necessary information in one efficient call.
    """
    return (
        db.query(models.Shipment)
        .join(models.Vehicle)
        .filter(models.Vehicle.driver_id == driver_id)
        .options(
            joinedload(models.Shipment.order).joinedload(models.Order.customer)
        )
        .order_by(models.Shipment.shipped_at.desc())
        .all()
    )

def update_shipment_status(db: Session, shipment_id: UUID, new_status: str, driver_id: UUID):
    """
    Updates a shipment's status, with crucial business logic and security checks.
    """
    # 1. Find the shipment and eagerly load related data for efficiency
    shipment = db.query(models.Shipment).options(
        joinedload(models.Shipment.vehicle),
        joinedload(models.Shipment.order)
    ).filter(models.Shipment.shipment_id == shipment_id).first()

    if not shipment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found.")

    # 2. SECURITY CHECK: Ensure the person updating is the assigned driver
    if not shipment.vehicle or shipment.vehicle.driver_id != driver_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this shipment.")

    # 3. Update the statuses
    shipment.status = new_status
    shipment.order.status = new_status

    # 4. CRITICAL BUSINESS LOGIC: Perform actions based on the new status
    if new_status == "delivered":
        # Set the actual delivery date on the order
        shipment.order.actual_delivery_date = datetime.now(timezone.utc)
        # Free up the vehicle to be used for another delivery
        shipment.vehicle.status = "active"

    # 5. Commit the transaction
    db.commit()
    db.refresh(shipment)
    return shipment