import os
from supabase import create_client, Client
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Configuration ---
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SupABASE URL/Key must be set.")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def embed_and_ingest_documents():
    """Finds text files, chunks them, generates embeddings, and uploads to Supabase."""
    print("--- Starting document embedding and ingestion... ---")
    print(f"Loading embedding model: '{EMBEDDING_MODEL_NAME}'")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    documents_to_insert = []
    for root, _, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                print(f"\nProcessing file: {file}")
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                chunks = text_splitter.split_text(content)
                print(f"Split document into {len(chunks)} chunks.")
                embeddings = model.encode(chunks, show_progress_bar=True)
                for i, chunk_text in enumerate(chunks):
                    documents_to_insert.append(
                        {
                            "source_type": "incident_report",
                            "source_id": file,
                            "region_id": "SoCal",
                            "ts": "2025-09-27 14:30:00",
                            "chunk_index": i,
                            "text_snippet": chunk_text,
                            "embedding_model": EMBEDDING_MODEL_NAME,
                            "embedding": embeddings[i].tolist(),
                        }
                    )

    if documents_to_insert:
        print(
            f"\nClearing old documents and inserting {len(documents_to_insert)} new chunks..."
        )
        supabase.table("documents").delete().neq(
            "doc_id", "00000000-0000-0000-0000-000000000000"
        ).execute()
        response = supabase.table("documents").insert(documents_to_insert).execute()
        if hasattr(response, "error") and response.error:
            print(f"!!! ERROR DURING INSERTION: {response.error.message}")
        else:
            print("Successfully inserted document chunks.")
    else:
        print("No new documents found to process.")


if __name__ == "__main__":
    embed_and_ingest_documents()
