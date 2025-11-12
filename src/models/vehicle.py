from sqlalchemy import Column, String, Numeric, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import uuid4
from ..database import Base

class Vehicle(Base):
    """Vehicle model updated with a foreign key relationship to the driver (customer)."""
    __tablename__ = "vehicles"
    __table_args__ = {"schema": "public"}
    
    vehicle_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    vehicle_type = Column(Enum('Truck', 'Van', 'Bike', name='vehicle_type_enum', create_type=False))
    capacity_kg = Column(Numeric)
    capacity_volume_cm3 = Column(Numeric)
    fuel_type = Column(Enum('EV', 'Diesel', 'Petrol', 'CNG', name='fuel_type_enum', create_type=False))
    
    plate_number = Column(String, unique=True)
    current_location = Column(String)
    status = Column(Enum('active', 'inactive', 'maintenance', 'in-transit', name='vehicle_status', create_type=False), nullable=False, server_default='active')
    
    # --- NEW: Relationship to Customer table ---
    driver_id = Column(PG_UUID(as_uuid=True), ForeignKey('public.customers.customer_id'), nullable=True)
    driver = relationship("Customer")
    
    def __repr__(self):
        return f"<Vehicle(type={self.vehicle_type}, plate={self.plate_number})>"