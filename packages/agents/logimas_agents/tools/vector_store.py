import os
from typing import List, Any
from dotenv import load_dotenv
import psycopg2

from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

# --- Configuration ---
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

if not DB_CONNECTION_STRING:
    raise ValueError("DB_CONNECTION_STRING must be set in the .env file.")

# --- Custom Retriever Definition ---

class DirectPostgresRetriever(BaseRetriever):
    """
    A custom retriever that connects directly to PostgreSQL using psycopg2
    to execute the vector search.
    """
    embedding_model: Any
    db_uri: str
    k_results: int = 5

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        
        query_embedding = self.embedding_model.embed_query(query)
        embedding_string = str(query_embedding)
        conn = None
        try:
            conn = psycopg2.connect(self.db_uri)
            cur = conn.cursor()
            sql_query = "SELECT * FROM match_documents(%s::vector, %s, '{}'::jsonb);"
            cur.execute(sql_query, (embedding_string, self.k_results))
            results = cur.fetchall()
            documents = []
            for row in results:
                doc_id, content, metadata, similarity = row
                metadata['similarity_score'] = similarity
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
            return documents
        except Exception as e:
            print(f"An error occurred in DirectPostgresRetriever: {e}")
            return []
        finally:
            if conn:
                conn.close()

# --- Factory Function for Retriever ---

def get_retriever(k_results: int = 5) -> BaseRetriever:
    """
    Initializes and returns our custom direct-to-database retriever.
    """
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return DirectPostgresRetriever(
        embedding_model=embedding_model,
        db_uri=DB_CONNECTION_STRING,
        k_results=k_results
    )

# --- NEW REUSABLE EMBEDDING UTILITY ---

# Singleton pattern to ensure the model is loaded only once per server start.
_embedding_model_instance = None
def get_embedding_model():
    """Loads the SentenceTransformer model only once."""
    global _embedding_model_instance
    if _embedding_model_instance is None:
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        print(f"--- Loading embedding model ({model_name}) for utility use... ---")
        _embedding_model_instance = SentenceTransformer(model_name)
    return _embedding_model_instance

def create_embedding(text: str) -> list[float]:
    """
    Takes a string of text and returns its vector embedding as a list of floats.
    This function is used by the /incidents endpoint in main.py.
    """
    model = get_embedding_model()
    return model.encode(text).tolist()