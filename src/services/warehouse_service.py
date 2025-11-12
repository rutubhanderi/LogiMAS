from sqlalchemy.orm import Session
from uuid import UUID
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from .. import models
from ..schemas import warehouse as warehouse_schema

# --- NEW: Geocoding Function ---
def get_coords_from_city(city: str):
    """Converts a city/region name into latitude and longitude."""
    try:
        geolocator = Nominatim(user_agent="logimas_warehouse_app")
        location = geolocator.geocode(city, timeout=10)
        if location:
            return location.latitude, location.longitude
        return None, None
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None, None

def get_all_warehouses(db: Session):
    return db.query(models.Warehouse).order_by(models.Warehouse.name).all()

# --- MODIFIED: Create function now handles geocoding ---
def create_warehouse(db: Session, warehouse: warehouse_schema.WarehouseCreate):
    lat, lon = get_coords_from_city(warehouse.region)
    if not lat or not lon:
        raise ValueError(f"Could not find coordinates for the region '{warehouse.region}'. Please provide a valid city name.")
    
    warehouse.lat = lat
    warehouse.lon = lon
    
    db_warehouse = models.Warehouse(**warehouse.dict())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

# --- MODIFIED: Update function now handles geocoding if region changes ---
def update_warehouse(db: Session, warehouse_id: UUID, warehouse_update: warehouse_schema.WarehouseUpdate):
    db_warehouse = db.query(models.Warehouse).filter(models.Warehouse.warehouse_id == warehouse_id).first()
    if not db_warehouse:
        return None

    update_data = warehouse_update.dict(exclude_unset=True)

    # If the region is being changed, re-geocode
    if 'region' in update_data and update_data['region'] != db_warehouse.region:
        lat, lon = get_coords_from_city(update_data['region'])
        if not lat or not lon:
            raise ValueError(f"Could not find coordinates for the new region '{update_data['region']}'.")
        update_data['lat'] = lat
        update_data['lon'] = lon

    for key, value in update_data.items():
        setattr(db_warehouse, key, value)
        
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

def delete_warehouse(db: Session, warehouse_id: UUID):
    db_warehouse = db.query(models.Warehouse).filter(models.Warehouse.warehouse_id == warehouse_id).first()
    if not db_warehouse:
        return False
    db.delete(db_warehouse)
    db.commit()
    return True