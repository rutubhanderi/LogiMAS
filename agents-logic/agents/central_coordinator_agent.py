from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("MODEL")
temprature = os.getenv("TEMPERATURE")

llm = ChatGroq(model=model, temperature=temprature, groq_api_key=groq_api_key)

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
""",
)

routing_chain = routing_prompt | llm


queries = [
    "Find the fastest delivery route to Bangalore",
    "Check if we have enough stock for next week's orders",
    "Reduce the cost of delivering 100 packages to Mumbai",
    "Given the current weather disruptions, suggest the best route and cost estimate for urgent medical supplies to Chennai by tomorrow morning.",
    "Forecast inventory shortages for the next quarter and recommend restocking strategies for all warehouses in North India.",
    "Optimize the delivery schedule for 500 packages across 10 cities, minimizing both time and transportation costs.",
    "If the fuel prices increase by 10%, how should we adjust our delivery routes and schedules to maintain profitability?",
    "Analyze last month's delivery data and suggest improvements to reduce delays and costs for perishable goods.",
    "What is the best way to balance inventory between our Delhi and Mumbai warehouses to avoid overstock and stockouts?",
    "Given a sudden spike in demand for electronics in Bangalore, how should we adjust our supply chain to meet the demand efficiently?",
]

for q in queries:
    result = routing_chain.invoke({"query": q})
    print(f"Query: {q}")
    print(f"Routed to: {result.content.strip()}\n")
