from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from supabase import create_client, Client
from ...config import settings

router = APIRouter()

# Dependency to get Supabase client
def get_supabase_client() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise HTTPException(status_code=500, detail="Supabase configuration missing")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

class AnalyticsResponse(BaseModel):
    total_revenue: float
    delivery_success_rate: float
    avg_delivery_time: str
    customer_satisfaction: float
    revenue_trend: Dict[str, float]
    delivery_status_distribution: Dict[str, int]
    top_delivery_personnel: List[Dict[str, Any]]
    popular_routes: List[Dict[str, Any]]

@router.get("", response_model=AnalyticsResponse)
@router.get("/summary", response_model=AnalyticsResponse)
def get_analytics(supabase: Client = Depends(get_supabase_client)):
    """
    Retrieve the latest analytics summary data from Supabase.
    Both `/api/v1/analytics` and `/api/v1/analytics/summary` call this.
    """
    try:
        response = (
            supabase.table("analytics_summary")
            .select("*")
            .order("last_updated", desc=True)
            .limit(1)
            .execute()
        )

        if not response.data:
            return AnalyticsResponse(
                total_revenue=0.0,
                delivery_success_rate=0.0,
                avg_delivery_time="0 minutes",
                customer_satisfaction=0.0,
                revenue_trend={},
                delivery_status_distribution={},
                top_delivery_personnel=[],
                popular_routes=[],
            )

        summary = response.data[0]

        import json

        def safe_parse(field: Any) -> Dict:
            if isinstance(field, dict):
                return field
            try:
                return json.loads(field) if field else {}
            except:
                return {}

        revenue_trend = safe_parse(summary.get("revenue_trend_json", {}))
        status_dist = safe_parse(summary.get("delivery_status_distribution", {}))
        top_personnel_raw = safe_parse(summary.get("top_delivery_personnel", {}))
        popular_routes_raw = safe_parse(summary.get("popular_routes", {}))

        return AnalyticsResponse(
            total_revenue=float(summary.get("total_revenue", 0)),
            delivery_success_rate=float(summary.get("delivery_success_rate", 0)),
            avg_delivery_time=str(summary.get("avg_delivery_time", "0 minutes")),
            customer_satisfaction=float(summary.get("customer_satisfaction", 0)),
            revenue_trend=revenue_trend,
            delivery_status_distribution=status_dist,
            top_delivery_personnel=top_personnel_raw.get("personnel", []),
            popular_routes=popular_routes_raw.get("routes", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")
