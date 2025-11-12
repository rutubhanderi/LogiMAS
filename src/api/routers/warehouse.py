from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ... import database, security
from ...schemas import warehouse as warehouse_schema
from ...services import warehouse_service

router = APIRouter()

@router.get("/", response_model=List[warehouse_schema.WarehousePublic], summary="Get all warehouses (Admin Only)")
def list_warehouses(db: Session = Depends(database.get_db), current_user=Depends(security.get_admin_user)):
    return warehouse_service.get_all_warehouses(db)

@router.post("/", response_model=warehouse_schema.WarehousePublic, status_code=status.HTTP_201_CREATED, summary="Create a warehouse (Admin Only)")
def create_warehouse(warehouse: warehouse_schema.WarehouseCreate, db: Session = Depends(database.get_db), current_user=Depends(security.get_admin_user)):
    return warehouse_service.create_warehouse(db, warehouse)

@router.patch("/{warehouse_id}", response_model=warehouse_schema.WarehousePublic, summary="Update a warehouse (Admin Only)")
def update_warehouse(warehouse_id: UUID, warehouse_update: warehouse_schema.WarehouseUpdate, db: Session = Depends(database.get_db), current_user=Depends(security.get_admin_user)):
    updated = warehouse_service.update_warehouse(db, warehouse_id, warehouse_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return updated

@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a warehouse (Admin Only)")
def delete_warehouse(warehouse_id: UUID, db: Session = Depends(database.get_db), current_user=Depends(security.get_admin_user)):
    success = warehouse_service.delete_warehouse(db, warehouse_id)
    if not success:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return {"ok": True}