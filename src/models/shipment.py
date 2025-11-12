from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from ..database import Base


class Shipment(Base):
    """Shipment model for tracking deliveries"""
    __tablename__ = "shipments"
    __table_args__ = {"schema": "public"}
    
    shipment_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_id = Column(PG_UUID(as_uuid=True), ForeignKey('public.orders.order_id'))
    origin_warehouse_id = Column(PG_UUID(as_uuid=True), ForeignKey('public.warehouses.warehouse_id'))
    vehicle_id = Column(PG_UUID(as_uuid=True), ForeignKey('public.vehicles.vehicle_id'))
    shipped_at = Column(DateTime(timezone=True))
    expected_arrival = Column(DateTime(timezone=True))
    current_eta = Column(DateTime(timezone=True))
    status = Column(String)
    distance_km = Column(Numeric)
    
    # Relationships
    order = relationship("Order", backref="shipments")
    warehouse = relationship("Warehouse", backref="shipments")
    vehicle = relationship("Vehicle", backref="shipments")
    
    def __repr__(self):
        return f"<Shipment(shipment_id={self.shipment_id}, status={self.status})>"
