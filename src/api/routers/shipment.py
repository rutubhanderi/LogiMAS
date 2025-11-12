from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List 
from ... import security, database
from ...schemas import shipment as shipment_schema
from ...services import shipment_service
from ...models import Customer

router = APIRouter()

@router.post(
    "/",
    response_model=shipment_schema.ShipmentPublicSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new shipment for an order (Admin Only)",
    description="Creates a shipment by assigning a warehouse and vehicle to a pending order."
)
def create_shipment(
    shipment_data: shipment_schema.ShipmentCreateSchema,
    db: Session = Depends(database.get_db),
    # This endpoint is protected and can only be accessed by an admin
    current_user: Customer = Depends(security.get_admin_user)
):
    try:
        new_shipment = shipment_service.create_shipment_for_order(
            db=db,
            order_id=shipment_data.order_id
        )
        return new_shipment
    except HTTPException as e:
        # Re-raise known HTTP exceptions from the service layer
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.get(
    "/my-deliveries",
    response_model=List[shipment_schema.DriverShipmentDetailSchema],
    summary="Get all shipments assigned to the current driver",
    description="Lists all shipments for the currently authenticated delivery personnel."
)
def get_my_deliveries(
    db: Session = Depends(database.get_db),
    # This ensures only a logged-in user can access their own deliveries
    current_user: Customer = Depends(security.get_current_active_user)
):
    """
    Endpoint for a delivery driver to fetch their list of assigned shipments.
    """
    try:
        # The user's ID is taken directly from their authentication token
        return shipment_service.get_shipments_for_driver(db, driver_id=current_user.customer_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
@router.patch(
    "/{shipment_id}/status",
    response_model=shipment_schema.ShipmentPublicSchema,
    summary="Update a shipment's status (Driver Only)",
    description="Allows the assigned driver to update the status of their shipment (e.g., to 'delivered')."
)
def update_shipment_status_endpoint(
    shipment_id: UUID,
    status_update: shipment_schema.ShipmentStatusUpdate,
    db: Session = Depends(database.get_db),
    current_user: Customer = Depends(security.get_current_active_user)
):
    """
    Endpoint for a driver to update the status of a shipment.
    """
    try:
        updated_shipment = shipment_service.update_shipment_status(
            db=db,
            shipment_id=shipment_id,
            new_status=status_update.status.value,
            driver_id=current_user.customer_id
        )
        return updated_shipment
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )