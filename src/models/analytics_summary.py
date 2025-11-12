from sqlalchemy import Column, Integer, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import INTERVAL, JSONB
from ..database import Base  # Assuming Base is defined in src/database.py

class AnalyticsSummary(Base):
    __tablename__ = "analytics_summary"

    id = Column(Integer, primary_key=True, index=True)
    total_revenue = Column(Numeric, default=0)
    delivery_success_rate = Column(Numeric, default=0)
    avg_delivery_time = Column(INTERVAL, default="0 minutes")
    customer_satisfaction = Column(Numeric, default=0)
    revenue_trend_json = Column(JSONB, default=dict)
    delivery_status_distribution = Column(JSONB, default=dict)
    top_delivery_personnel = Column(JSONB, default=dict)
    popular_routes = Column(JSONB, default=dict)
    last_updated = Column(DateTime(timezone=True), default=None)
    period = Column(String(10), default="30d")