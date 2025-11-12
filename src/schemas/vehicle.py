from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from enum import Enum

class VehicleType(str, Enum):
    truck = "Truck"; van = "Van"; bike = "Bike"
class FuelType(str, Enum):
    EV = "EV"; diesel = "Diesel"; petrol = "Petrol"; CNG = "CNG"
class VehicleStatus(str, Enum):
    active = "active"; inactive = "inactive"; maintenance = "maintenance"; in_transit = "in-transit"

# --- NEW: A schema to represent driver info in the response ---
class DriverInfo(BaseModel):
    customer_id: UUID
    name: str
    class Config:
        from_attributes = True

class VehicleBase(BaseModel):
    vehicle_type: VehicleType
    plate_number: str = Field(..., max_length=20)
    capacity_kg: float = Field(..., gt=0)
    fuel_type: FuelType
    current_location: Optional[str] = None
    status: VehicleStatus = 'active'
    # --- MODIFIED: We now expect a driver_id (UUID) ---
    driver_id: Optional[UUID] = None

class VehicleCreate(VehicleBase):
    pass
class VehicleUpdate(VehicleBase):
    pass

# --- MODIFIED: The public schema now returns a nested driver object ---
class VehiclePublic(VehicleBase):
    vehicle_id: UUID
    driver: Optional[DriverInfo] = None
    class Config:
        from_attributes = True