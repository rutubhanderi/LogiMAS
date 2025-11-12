import os
from typing import List, Any
from dotenv import load_dotenv
import psycopg2
from pgvector.psycopg2 import register_vector

from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from ...config import settings

DB_CONNECTION_STRING = settings.DB_CONNECTION_STRING
EMBEDDING_MODEL_NAME = settings.EMBEDDING_MODEL_NAME or "all-MiniLM-L6-v2"

# --- Custom Retriever Definition ---

class DirectPostgresRetriever(BaseRetriever):
    """
    A custom retriever that connects directly to PostgreSQL using psycopg2
    to execute a vector similarity search with the correct column names.
    """

    embedding_model: Any
    db_uri: str
    k_results: int = 5

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:

        query_embedding = self.embedding_model.embed_query(query)
        conn = None
        try:
            conn = psycopg2.connect(self.db_uri)
            register_vector(conn)
            cur = conn.cursor()
            sql_query = """
                SELECT
                    doc_id,
                    text_snippet,
                    source_type,
                    1 - (embedding <=> %s::vector) AS similarity
                FROM
                    documents
                ORDER BY
                    embedding <=> %s::vector
                LIMIT %s;
            """

            cur.execute(sql_query, (query_embedding, query_embedding, self.k_results))

            results = cur.fetchall()
            documents = []
            for row in results:
                doc_id, content, source, similarity = row
                metadata = {
                    "doc_id": str(doc_id),
                    "source": source,
                    "similarity_score": similarity,
                }
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
            return documents
        except Exception as e:
            print(f"An error occurred in DirectPostgresRetriever: {e}")
            raise
        finally:
            if conn:
                conn.close()


def get_retriever(k_results: int = 5) -> BaseRetriever:
    """
    Initializes and returns our custom direct-to-database retriever.
    """
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return DirectPostgresRetriever(
        embedding_model=embedding_model,
        db_uri=DB_CONNECTION_STRING,
        k_results=k_results,
    )

# --- Reusable Embedding Utility (Unchanged) ---

_embedding_model_instance = None

def get_embedding_model():
    """Loads the SentenceTransformer model only once."""
    global _embedding_model_instance
    if _embedding_model_instance is None:
        model_name = EMBEDDING_MODEL_NAME
        print(f"--- Loading embedding model ({model_name}) for utility use... ---")
        _embedding_model_instance = SentenceTransformer(model_name)
    return _embedding_model_instance


def create_embedding(text: str) -> list[float]:
    """
    Takes a string of text and returns its vector embedding as a list of floats.
    """
    model = get_embedding_model()
    return model.encode(text).tolist()