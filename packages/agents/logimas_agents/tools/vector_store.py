# File: packages/agents/logimas_agents/tools/vector_store.py
import os
from typing import List, Any
from dotenv import load_dotenv
import psycopg2

from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

# --- Configuration ---
# Load environment variables from the root .env file
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
    to bypass the Supabase client bug and execute the vector search.
    """
    embedding_model: Any
    db_uri: str
    k_results: int = 4

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        
        
        # 1. Embed the user's query using the sentence-transformer model
        query_embedding = self.embedding_model.embed_query(query)
        
        # 2. Format the embedding into a string '[...]' that pgvector expects
        embedding_string = str(query_embedding)

        conn = None
        try:
            # 3. Connect directly to the database
            conn = psycopg2.connect(self.db_uri)
            cur = conn.cursor()

            # 4. Define the SQL to call our function with explicit casting
            sql_query = """
            SELECT * FROM match_documents(%s::vector, %s, '{}'::jsonb);
            """
            
            # 5. Execute the query safely
            cur.execute(sql_query, (embedding_string, self.k_results))
            results = cur.fetchall()

            # 6. Process the results and format them as LangChain Document objects
            documents = []
            for row in results:
                # The function returns: id, content, metadata, similarity
                doc_id, content, metadata, similarity = row
                # We add the similarity score to the metadata for potential use later
                metadata['similarity_score'] = similarity
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
            
            return documents

        except Exception as e:
            print(f"An error occurred in DirectPostgresRetriever: {e}")
            return [] # Return an empty list in case of an error
        finally:
            if conn:
                cur.close()
                conn.close()

# --- Factory Function ---
# The rest of our application will call this function, so no other files need to change.
def get_retriever(k_results: int = 4) -> BaseRetriever:
    """
    Initializes and returns our custom direct-to-database retriever.
    """
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    retriever = DirectPostgresRetriever(
        embedding_model=embedding_model,
        db_uri=DB_CONNECTION_STRING,
        k_results=k_results
    )
    return retriever