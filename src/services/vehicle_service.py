from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from .. import models
from ..schemas import vehicle as vehicle_schema

def get_all_vehicles(db: Session):
    """
    Fetches all vehicles from the database.

    Crucially, it uses `joinedload(models.Vehicle.driver)` to perform an efficient SQL JOIN.
    This fetches the related driver (from the 'customers' table) in the same query,
    preventing performance bottlenecks that would occur if each driver was fetched separately.
    """
    return db.query(models.Vehicle).options(joinedload(models.Vehicle.driver)).order_by(models.Vehicle.plate_number).all()


def create_vehicle(db: Session, vehicle: vehicle_schema.VehicleCreate):
    """
    Creates a new vehicle record in the database.

    It takes the validated data from the Pydantic schema, including the optional 'driver_id',
    and uses it to create a new SQLAlchemy model instance.
    """
    db_vehicle = models.Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def update_vehicle(db: Session, vehicle_id: UUID, vehicle_update: vehicle_schema.VehicleUpdate):
    """
    Updates an existing vehicle record by its ID.

    It finds the vehicle and applies only the fields that were provided in the update request.
    This correctly handles changing or un-assigning a driver by updating the 'driver_id'.
    """
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.vehicle_id == vehicle_id).first()
    if not db_vehicle:
        return None
        
    # Get the update data, excluding fields that were not sent in the request
    update_data = vehicle_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_vehicle, key, value)
        
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def delete_vehicle(db: Session, vehicle_id: UUID):
    """
    Deletes a vehicle record from the database by its ID.
    """
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.vehicle_id == vehicle_id).first()
    if not db_vehicle:
        return False
        
    db.delete(db_vehicle)
    db.commit()
    return True