from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class AnalyticsSummaryPublic(BaseModel):
    id: int
    total_revenue: float
    delivery_success_rate: float
    avg_delivery_time: Optional[str]
    customer_satisfaction: float
    revenue_trend_json: Optional[Dict[str, float]]
    delivery_status_distribution: Optional[Dict[str, int]]
    top_delivery_personnel: Optional[Dict[str, Any]]
    popular_routes: Optional[Dict[str, Any]]
    last_updated: Optional[datetime]
    period: Optional[str]

    class Config:
        from_attributes = True
