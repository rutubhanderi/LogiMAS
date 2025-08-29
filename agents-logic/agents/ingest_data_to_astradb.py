import os
import csv
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_astradb import AstraDBVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings   # ✅ HuggingFace embeddings


PRODUCTS_FILE = "C:/Users/ASUS/Desktop/BTech Projects/LogiMAS/agents-logic/data/products.csv"
ASTRA_DB_COLLECTION_NAME = "product_knowledge_base"


def ingest_data():
    """
    Reads data from products.csv, creates vector embeddings, and ingests them into Astra DB.
    """
    print("--- Starting Data Ingestion to Astra DB ---")
    load_dotenv()

    # 1. --- Check for necessary environment variables ---
    required_vars = [
        "ASTRA_DB_API_ENDPOINT",
        "ASTRA_DB_APPLICATION_TOKEN",
    ]
    for var in required_vars:
        if var not in os.environ:
            print(
                f"Error: Environment variable '{var}' not found. Please set it in your .env file."
            )
            return

    # 2. --- Initialize HuggingFace Embedding Model ---
    try:
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("✅ HuggingFace embedding model initialized.")
    except Exception as e:
        print(f"Error initializing HuggingFace embeddings: {e}")
        return

    # 3. --- Initialize the AstraDB Vector Store ---
    try:
        vstore = AstraDBVectorStore(
            collection_name=ASTRA_DB_COLLECTION_NAME,
            api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
            token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
            embedding=embedding_model,
        )
        print(f"✅ AstraDBVectorStore initialized for collection '{ASTRA_DB_COLLECTION_NAME}'.")
    except Exception as e:
        print(f"Error initializing AstraDBVectorStore: {e}")
        return

    # 4. --- Read CSV and Create LangChain Documents ---
    if not os.path.exists(PRODUCTS_FILE):
        print(f"Error: The file '{PRODUCTS_FILE}' was not found.")
        print(
            "Please ensure you have a 'data' folder in your project directory containing 'products.csv'."
        )
        return

    print(f"Reading data from {PRODUCTS_FILE}...")
    documents_to_add = []
    with open(PRODUCTS_FILE, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            page_content = (
                f"Product Name: {row['name']}\n"
                f"Category: {row['category']}\n"
                f"Description: {row['description']}\n"
                f"Special Handling: {row['special_handling_instructions']}"
            )
            metadata = {
                "item_id": row["item_id"],
                "name": row["name"],
                "category": row["category"],
                "is_fragile": row["is_fragile"].lower() == "true",
                "is_hazardous": row["is_hazardous"].lower() == "true",
                "unit_weight_kg": float(row["unit_weight_kg"]),
                "dimensions_cm": row["dimensions_cm"],
                "supplier_id": row["supplier_id"],
                "manufacturing_cost_per_unit": float(
                    row["manufacturing_cost_per_unit"]
                ),
            }
            documents_to_add.append(
                Document(page_content=page_content, metadata=metadata)
            )

    print(f"Created {len(documents_to_add)} documents to be ingested.")

    # 5. --- Add Documents to Astra DB ---
    print("Ingesting documents into Astra DB (this may take a while)...")
    try:
        vstore.add_documents(documents_to_add, batch_size=20)
        print(f"✅ Successfully ingested {len(documents_to_add)} documents into Astra DB.")
    except Exception as e:
        print(f"Error ingesting documents: {e}")
        return

    print("--- Ingestion Complete ---")


if __name__ == "__main__":
    ingest_data()
