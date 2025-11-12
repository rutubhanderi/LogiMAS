from sqlalchemy import Column, String, Numeric, DateTime
from datetime import datetime
from ..database import Base


class FuelPrice(Base):
    """Fuel price model for tracking fuel costs"""
    __tablename__ = "fuel_prices"
    __table_args__ = {"schema": "public"}
    
    fuel_type = Column(String, primary_key=True)
    cost_per_liter = Column(Numeric, nullable=False)
    last_updated = Column(DateTime(timezone=True), default=datetime.now)
    
    def __repr__(self):
        return f"<FuelPrice(fuel_type={self.fuel_type}, cost={self.cost_per_liter})>"
