import os
import csv
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBStore

# --- Configuration ---
PRODUCTS_FILE = "products.csv"
ASTRA_DB_COLLECTION_NAME = "product_knowledge_base"

def ingest_data():
    """
    Reads data from products.csv, creates vector embeddings, and ingests them into Astra DB.
    """
    print("--- Starting Data Ingestion to Astra DB ---")
    load_dotenv()

    # 1. --- Check for necessary environment variables ---
    required_vars = ["ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN", "OPENAI_API_KEY"]
    for var in required_vars:
        if var not in os.environ:
            print(f"Error: Environment variable '{var}' not found. Please set it in your .env file.")
            return

    # 2. --- Initialize the Embedding Model ---
    try:
        embedding_model = OpenAIEmbeddings()
        print("✅ OpenAI Embedding model initialized.")
    except Exception as e:
        print(f"Error initializing OpenAI embeddings: {e}")
        return

    # 3. --- Initialize the AstraDB Vector Store ---
    # This will create the collection in Astra DB if it doesn't exist.
    vstore = AstraDBStore(
        collection_name=ASTRA_DB_COLLECTION_NAME,
        embedding=embedding_model,
        api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
        token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
    )
    print(f"✅ AstraDBStore initialized for collection '{ASTRA_DB_COLLECTION_NAME}'.")

    # 4. --- Read CSV and Create LangChain Documents ---
    if not os.path.exists(PRODUCTS_FILE):
        print(f"Error: {PRODUCTS_FILE} not found.")
        return

    print(f"Reading data from {PRODUCTS_FILE}...")
    documents_to_add = []
    with open(PRODUCTS_FILE, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            # Create a rich text block for vectorization. This is what the semantic search will match against.
            page_content = (
                f"Product Name: {row['name']}\n"
                f"Category: {row['category']}\n"
                f"Description: {row['description']}\n"
                f"Special Handling: {row['special_handling_instructions']}"
            )

            # Keep all other columns as metadata for filtering and retrieval.
            metadata = {
                "item_id": row['item_id'],
                "name": row['name'],
                "category": row['category'],
                "is_fragile": row['is_fragile'].lower() == 'true',
                "is_hazardous": row['is_hazardous'].lower() == 'true',
                "unit_weight_kg": float(row['unit_weight_kg']),
                "dimensions_cm": row['dimensions_cm'],
                "supplier_id": row['supplier_id'],
                "manufacturing_cost_per_unit": float(row['manufacturing_cost_per_unit'])
            }
            documents_to_add.append(Document(page_content=page_content, metadata=metadata))

    print(f"Created {len(documents_to_add)} documents to be ingested.")

    # 5. --- Add Documents to Astra DB ---
    # This step generates embeddings and writes the data. It can take time.
    # For very large datasets, add documents in batches.
    print("Ingesting documents into Astra DB (this may take a while)...")
    vstore.add_documents(documents_to_add, batch_size=20)
    print(f"✅ Successfully ingested {len(documents_to_add)} documents into Astra DB.")
    print("--- Ingestion Complete ---")

if __name__ == "__main__":
    ingest_data()