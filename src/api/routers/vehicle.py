from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ... import database, security
from ...schemas import vehicle as vehicle_schema
from ...services import vehicle_service

router = APIRouter()

@router.get("/", response_model=List[vehicle_schema.VehiclePublic], summary="Get all vehicles (Admin Only)")
def list_vehicles(db: Session = Depends(database.get_db), current_user=Depends(security.get_admin_user)):
    return vehicle_service.get_all_vehicles(db)

@router.post("/", response_model=vehicle_schema.VehiclePublic, status_code=status.HTTP_201_CREATED, summary="Create a vehicle (Admin Only)")
def create_vehicle(vehicle: vehicle_schema.VehicleCreate, db: Session = Depends(database.get_db), current_user=Depends(security.get_admin_user)):
    return vehicle_service.create_vehicle(db, vehicle)

@router.patch("/{vehicle_id}", response_model=vehicle_schema.VehiclePublic, summary="Update a vehicle (Admin Only)")
def update_vehicle(vehicle_id: UUID, vehicle_update: vehicle_schema.VehicleUpdate, db: Session = Depends(database.get_db), current_user=Depends(security.get_admin_user)):
    updated = vehicle_service.update_vehicle(db, vehicle_id, vehicle_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return updated

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a vehicle (Admin Only)")
def delete_vehicle(vehicle_id: UUID, db: Session = Depends(database.get_db), current_user=Depends(security.get_admin_user)):
    success = vehicle_service.delete_vehicle(db, vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"ok": True}