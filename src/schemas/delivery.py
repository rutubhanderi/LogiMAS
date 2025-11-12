# api/schemas/delivery.py
from pydantic import BaseModel

class IncidentReport(BaseModel):
    shipmentId: str
    incidentType: str
    description: str
    severity: str