from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class WarehouseBase(BaseModel):
    name: str
    region: str
    capacity_sq_ft: Optional[float] = Field(None, gt=0)
    utilization_pct: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = 'active'
    
    # --- MODIFIED: Lat and Lon are now optional on create/update ---
    lat: Optional[float] = None
    lon: Optional[float] = None

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(WarehouseBase):
    pass

class WarehousePublic(WarehouseBase):
    warehouse_id: UUID

    class Config:
        from_attributes = True