from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0,groq_api_key=groq_api_key)

# Prompt template
routing_prompt = PromptTemplate(
    input_variables=["query"],
    template="""
You are a coordinator agent in a logistics system.
Your task is to read the user's query and decide which specialized agent should handle it.

Specialized agents:
1. Mobility Agent - Optimizes delivery routes using live traffic and weather data.
2. Inventory & Supply Agent - Monitors stock levels, predicts demand, schedules restocking.
3. Cost Optimization Agent - Minimizes transportation and handling costs by suggesting efficient delivery strategies.

Rules:
- Output only the agent name, nothing else.

User Query: {query}
Answer:
"""
)

routing_chain = routing_prompt | llm

queries = [
    "Find the fastest delivery route to Bangalore",
    "Check if we have enough stock for next week's orders",
    "Reduce the cost of delivering 100 packages to Mumbai"
]

for q in queries:
    result = routing_chain.invoke({"query": q})
    print(f"Query: {q}")
    print(f"Routed to: {result.content.strip()}\n")