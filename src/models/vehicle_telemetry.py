from sqlalchemy import Column, BigInteger, DateTime, Float, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from ..database import Base


class VehicleTelemetry(Base):
    """Vehicle telemetry model for real-time tracking"""
    __tablename__ = "vehicle_telemetry"
    __table_args__ = {"schema": "public"}
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    vehicle_id = Column(PG_UUID(as_uuid=True), ForeignKey('public.vehicles.vehicle_id'))
    ts = Column(DateTime(timezone=True), nullable=False)
    lat = Column(Float)
    lon = Column(Float)
    speed_kmph = Column(Numeric)
    fuel_pct = Column(Numeric)
    cargo_temp = Column(Numeric)
    
    # Relationship
    vehicle = relationship("Vehicle", backref="telemetry")
    
    def __repr__(self):
        return f"<VehicleTelemetry(vehicle_id={self.vehicle_id}, ts={self.ts})>"
