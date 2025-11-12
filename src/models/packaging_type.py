from sqlalchemy import Column, String, Numeric, Computed
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import uuid4
from ..database import Base


class PackagingType(Base):
    """Packaging type model with auto-calculated volume"""
    __tablename__ = "packaging_types"
    __table_args__ = {"schema": "public"}
    
    packaging_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    length_cm = Column(Numeric, nullable=False)
    width_cm = Column(Numeric, nullable=False)
    height_cm = Column(Numeric, nullable=False)
    # Generated column - automatically calculated
    volume_cm3 = Column(Numeric, Computed("(length_cm * width_cm * height_cm)"))
    cost_per_unit = Column(Numeric)
    
    def __repr__(self):
        return f"<PackagingType(name={self.name}, volume={self.volume_cm3})>"
