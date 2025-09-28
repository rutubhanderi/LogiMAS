import os
from supabase import create_client, Client
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Configuration ---
# Load environment variables from the root .env file
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in the .env file.")

# Path to the unstructured data
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase client initialized.")


def embed_and_ingest():
    """
    Finds text files, chunks them, generates embeddings, and uploads to Supabase.
    """
    print(f"Loading embedding model: '{EMBEDDING_MODEL_NAME}'")
    # This will download the model from Hugging Face the first time it's run
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print("Model loaded successfully.")

    # A text splitter for breaking down large documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Max size of a chunk in characters
        chunk_overlap=50,  # Characters to overlap between chunks
        length_function=len,
    )

    documents_to_insert = []

    # Walk through the raw data directory to find text files
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                print(f"\n--- Processing file: {file} ---")

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Split the document into chunks
                chunks = text_splitter.split_text(content)
                print(f"Split document into {len(chunks)} chunks.")

                # Generate embeddings for each chunk
                print("Generating embeddings...")
                embeddings = model.encode(chunks, show_progress_bar=True)

                # Prepare records for insertion
                for i, chunk_text in enumerate(chunks):
                    record = {
                        "source_type": "incident_report",
                        "source_id": file,
                        "region_id": "SoCal",  # Example metadata
                        "ts": "2025-09-27 14:30:00",  # Example metadata
                        "chunk_index": i,
                        "text_snippet": chunk_text,
                        "embedding_model": EMBEDDING_MODEL_NAME,
                        # Convert numpy array to list for JSON compatibility
                        "embedding": embeddings[i].tolist(),
                    }
                    documents_to_insert.append(record)

    # --- Batch insert into Supabase ---
    if documents_to_insert:
        print(
            f"\nAttempting to insert {len(documents_to_insert)} document chunks into Supabase..."
        )
        try:
            response = supabase.table("documents").insert(documents_to_insert).execute()
            if hasattr(response, "error") and response.error:
                raise Exception(f"API Error: {response.error.message}")

            print("Successfully inserted document chunks into the 'documents' table.")
        except Exception as e:
            print(f"!!!!!!!! AN ERROR OCCURRED DURING INSERTION !!!!!!!!")
            print(str(e))
    else:
        print("No new documents found to process.")


if __name__ == "__main__":
    embed_and_ingest()
