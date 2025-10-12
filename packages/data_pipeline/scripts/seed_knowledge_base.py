"""
Seed Knowledge Base Documents
Populates the documents table with logistics knowledge for RAG
"""

import os
import json
from supabase import create_client
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in .env file")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize embedding model
print("Loading embedding model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("✓ Model loaded")

# Sample logistics knowledge base documents
KNOWLEDGE_DOCS = [
    {
        "source_type": "policy",
        "source_id": "POL-001",
        "region_id": "US-WEST",
        "text_snippet": "Standard delivery time for domestic shipments is 3-5 business days. Express delivery is available for 1-2 business day delivery at an additional cost.",
    },
    {
        "source_type": "policy",
        "source_id": "POL-002",
        "region_id": "US-EAST",
        "text_snippet": "All packages must be properly labeled with tracking numbers. Packages without proper labels will be held at the warehouse until corrected.",
    },
    {
        "source_type": "procedure",
        "source_id": "PROC-001",
        "region_id": "GLOBAL",
        "text_snippet": "In case of delivery delays, customers should be notified within 2 hours of the expected delay. Provide updated ETA and reason for delay.",
    },
    {
        "source_type": "procedure",
        "source_id": "PROC-002",
        "region_id": "GLOBAL",
        "text_snippet": "Damaged packages must be reported immediately. Take photos of the damage, document the shipment ID, and file an incident report within 24 hours.",
    },
    {
        "source_type": "policy",
        "source_id": "POL-003",
        "region_id": "US-CENTRAL",
        "text_snippet": "Maximum package weight is 150 lbs for standard delivery. Packages exceeding this weight require special handling and freight services.",
    },
    {
        "source_type": "faq",
        "source_id": "FAQ-001",
        "region_id": "GLOBAL",
        "text_snippet": "Q: How do I track my shipment? A: Use your shipment ID on our tracking page. You'll see real-time location, estimated delivery time, and delivery status.",
    },
    {
        "source_type": "faq",
        "source_id": "FAQ-002",
        "region_id": "GLOBAL",
        "text_snippet": "Q: What should I do if my package is lost? A: Contact customer service immediately with your shipment ID. We'll investigate and provide a resolution within 48 hours.",
    },
    {
        "source_type": "policy",
        "source_id": "POL-004",
        "region_id": "GLOBAL",
        "text_snippet": "Hazardous materials require special documentation and handling. Contact our hazmat team before shipping chemicals, batteries, or flammable materials.",
    },
    {
        "source_type": "procedure",
        "source_id": "PROC-003",
        "region_id": "GLOBAL",
        "text_snippet": "Vehicle maintenance checks must be performed every 5,000 miles or monthly, whichever comes first. Check tire pressure, oil levels, and brake functionality.",
    },
    {
        "source_type": "policy",
        "source_id": "POL-005",
        "region_id": "GLOBAL",
        "text_snippet": "Delivery drivers must obtain signature confirmation for packages valued over $500. Photo proof of delivery is acceptable for lower-value packages.",
    },
    {
        "source_type": "faq",
        "source_id": "FAQ-003",
        "region_id": "GLOBAL",
        "text_snippet": "Q: Can I change my delivery address? A: Yes, address changes are allowed up to 24 hours before scheduled delivery. Contact customer service with your shipment ID.",
    },
    {
        "source_type": "procedure",
        "source_id": "PROC-004",
        "region_id": "GLOBAL",
        "text_snippet": "For temperature-sensitive shipments, maintain cargo temperature between 35-45°F. Monitor temperature every 2 hours and log readings in the system.",
    },
    {
        "source_type": "policy",
        "source_id": "POL-006",
        "region_id": "US-WEST",
        "text_snippet": "Same-day delivery is available in major metropolitan areas for orders placed before 10 AM. Additional fees apply based on distance and urgency.",
    },
    {
        "source_type": "faq",
        "source_id": "FAQ-004",
        "region_id": "GLOBAL",
        "text_snippet": "Q: What are your operating hours? A: Our warehouses operate 24/7. Customer service is available Monday-Friday 8 AM - 8 PM, Saturday 9 AM - 5 PM.",
    },
    {
        "source_type": "procedure",
        "source_id": "PROC-005",
        "region_id": "GLOBAL",
        "text_snippet": "When loading vehicles, place heavy items on the bottom and distribute weight evenly. Secure all cargo with straps to prevent shifting during transport.",
    },
    {
        "source_type": "policy",
        "source_id": "POL-007",
        "region_id": "GLOBAL",
        "text_snippet": "Insurance is automatically included for shipments up to $100 value. Additional insurance can be purchased for high-value items at $1 per $100 of value.",
    },
    {
        "source_type": "faq",
        "source_id": "FAQ-005",
        "region_id": "GLOBAL",
        "text_snippet": "Q: How do I file a claim for a damaged package? A: Submit photos of the damage, original packaging, and shipment ID through our claims portal within 7 days of delivery.",
    },
    {
        "source_type": "procedure",
        "source_id": "PROC-006",
        "region_id": "GLOBAL",
        "text_snippet": "Route optimization should be performed daily before 6 AM. Consider traffic patterns, delivery windows, and vehicle capacity when planning routes.",
    },
    {
        "source_type": "policy",
        "source_id": "POL-008",
        "region_id": "GLOBAL",
        "text_snippet": "Returns are accepted within 30 days of delivery. Items must be in original packaging and unused. Return shipping labels can be generated online.",
    },
    {
        "source_type": "faq",
        "source_id": "FAQ-006",
        "region_id": "GLOBAL",
        "text_snippet": "Q: Do you deliver on weekends? A: Yes, Saturday delivery is available in most areas. Sunday delivery is available in select metropolitan areas for an additional fee.",
    },
]

def create_embeddings_and_insert():
    """Create embeddings for documents and insert into database"""
    print(f"\n--- Seeding {len(KNOWLEDGE_DOCS)} Knowledge Base Documents ---")
    
    documents_to_insert = []
    
    for idx, doc in enumerate(KNOWLEDGE_DOCS, 1):
        print(f"Processing document {idx}/{len(KNOWLEDGE_DOCS)}: {doc['source_id']}")
        
        # Create embedding
        embedding = model.encode(doc["text_snippet"])
        embedding_list = embedding.tolist()
        
        # Prepare document for insertion
        doc_data = {
            "source_type": doc["source_type"],
            "source_id": doc["source_id"],
            "region_id": doc["region_id"],
            "text_snippet": doc["text_snippet"],
            "chunk_index": 0,
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding": embedding_list,
        }
        
        documents_to_insert.append(doc_data)
    
    # Insert all documents
    print("\n--- Uploading to Supabase ---")
    try:
        response = supabase.table("documents").insert(documents_to_insert).execute()
        print(f"✓ Successfully inserted {len(documents_to_insert)} documents")
        return True
    except Exception as e:
        print(f"❌ Error inserting documents: {str(e)}")
        return False

def main():
    print("="*60)
    print("KNOWLEDGE BASE SEEDING")
    print("="*60)
    
    # Clear existing documents (optional)
    try:
        print("\n--- Clearing existing documents ---")
        supabase.table("documents").delete().neq("doc_id", "00000000-0000-0000-0000-000000000000").execute()
        print("✓ Cleared existing documents")
    except Exception as e:
        print(f"⚠ Warning: {str(e)}")
    
    # Seed documents
    success = create_embeddings_and_insert()
    
    if success:
        print("\n" + "="*60)
        print("✓ KNOWLEDGE BASE SEEDING COMPLETE!")
        print("="*60)
    else:
        print("\n❌ Seeding failed")

if __name__ == "__main__":
    main()
