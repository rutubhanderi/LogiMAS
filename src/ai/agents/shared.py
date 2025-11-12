# This file was not provided in your input, but it's referenced in multiple agents (e.g., from .shared import llm).
# I've inferred and created a basic implementation based on common patterns in the code (using Groq LLM).
# Adjust as needed if you have the exact code.

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from ...config import settings  # Adjusted to use project's config.py

# Load .env if not already loaded (though project's config.py handles most env vars)
load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Common model from your code patterns; adjust if different
    api_key=settings.GROQ_API_KEY,  # Use from config
    temperature=0.0,  # Default for deterministic responses; adjust as needed
)
