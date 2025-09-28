# File: packages/agents/test_direct_db.py (Final, Corrected Version)
import psycopg2
import random
import json

# !!! IMPORTANT: PASTE YOUR FULL DATABASE CONNECTION STRING FROM THE SUPABASE DASHBOARD HERE !!!
DB_CONNECTION_STRING = "postgresql://postgres:TeriMKC@db.dvbhuyhfqwedirgsgvjg.supabase.co:5432/postgres" # Make sure this is still correct

print("--- Starting Final Direct Database Connection Test ---")

try:
    conn = psycopg2.connect(DB_CONNECTION_STRING)
    print(">>> Successfully connected to the PostgreSQL database.")
    cur = conn.cursor()

    random_embedding = [random.random() for _ in range(384)]
    match_count = 3

    # CRITICAL FIX: Format the embedding as a JSON-style array string '[...]'
    # which is what the pgvector extension expects.
    embedding_string = str(random_embedding)
    
    sql_query = """
    SELECT * FROM match_documents(%s::vector, %s, '{}'::jsonb);
    """

    print("\nExecuting function with JSON-style vector format...")
    cur.execute(sql_query, (embedding_string, match_count))
    
    results = cur.fetchall()

    print("\n--- ✅ TEST SUCCEEDED ---")
    print(f"Function executed successfully and returned {len(results)} rows.")
    for i, row in enumerate(results):
        print(f"Row {i+1}: {row}")

    cur.close()
    conn.close()
    print("\nConnection closed.")

except Exception as e:
    print("\n--- ❌ TEST FAILED ---")
    print("An error occurred during the direct database test.")
    print("Error Type:", type(e).__name__)
    print("Error Details:", e)

print("\n--- Test Complete ---")