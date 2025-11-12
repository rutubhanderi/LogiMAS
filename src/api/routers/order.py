from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional 
from ... import security, database
from ...schemas import order as order_schema
from ...services import order_service
from ...models import Customer

router = APIRouter()

@router.post(
    "/",
    # --- MODIFIED: Response model is now just the public order schema ---
    response_model=order_schema.OrderPublicSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Place a new order",
    description="Creates a new order with a 'pending' status. Shipment is not created at this stage."
)
def place_order(
    order_data: order_schema.OrderCreateSchema,
    db: Session = Depends(database.get_db),
    current_user: Customer = Depends(security.get_current_active_user)
):
    try:
        # --- MODIFIED: Call the new, simpler service function ---
        new_order = order_service.create_order(
            db=db,
            order_data=order_data,
            customer_id=current_user.customer_id
        )
        # --- MODIFIED: Return only the new order ---
        return new_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        # Adding a print statement for server-side debugging
        print(f"An unexpected error occurred during order creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while placing the order."
        )


@router.get(
    "/",
    response_model=List[order_schema.OrderPublicSchema],
    summary="Get orders by status (Admin Only)",
    description="Retrieves a list of orders, filterable by status (e.g., 'pending', 'shipped')."
)
def get_orders(
    status: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: Customer = Depends(security.get_admin_user)
):
    """
    Endpoint for an admin to fetch orders. If a status is provided,
    it filters the orders by that status.
    """
    try:
        if status:
            orders = order_service.get_orders_by_status(db, status=status)
        else:
            # In the future, you could add a service to get all orders
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status filter is required.")
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )