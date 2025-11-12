# src/api/routes/delivery.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from sentence_transformers import SentenceTransformer

# Adjust imports based on your project structure
from ...database import get_db  # Correctly imports from src/database.py
from ...models.document import Document
from ...schemas.delivery import IncidentReport

# Load the sentence transformer model
embedding_model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(embedding_model_name)

router = APIRouter()

@router.post("/report-incident", status_code=201)
async def report_incident(incident: IncidentReport, db: Session = Depends(get_db)):
    """
    Receives an incident report, generates embeddings, and stores it in the database.
    """
    try:
        text_to_embed = (
            f"Incident Type: {incident.incidentType}. "
            f"Severity: {incident.severity}. "
            f"Description: {incident.description}"
        )
        embedding_vector = model.encode(text_to_embed).tolist()

        new_document = Document(
            source_type="incident_report",
            source_id=incident.shipmentId,
            ts=datetime.utcnow(),
            chunk_index=0,
            text_snippet=incident.description,
            embedding_model=embedding_model_name,
            embedding=embedding_vector
        )

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        return {"message": "Incident reported successfully", "doc_id": new_document.doc_id}

    except Exception as e:
        db.rollback()
        # It's good practice to log the error for debugging
        # import logging
        # logging.error(f"Error reporting incident: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while reporting the incident."
        )