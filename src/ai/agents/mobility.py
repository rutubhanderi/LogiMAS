from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from ..tools.vector_store import get_retriever  # Relative import remains the same
from .shared import llm  # Relative import remains the same

# A more specific prompt for the Mobility Agent
prompt_template = """
You are the Mobility Agent for LogiMAS, specializing in route analysis.
Your task is to analyze the provided context about traffic incidents and answer the user's question about a specific route.
Focus only on information relevant to the user's question. If no incidents are mentioned for the requested route, state that the route appears clear based on available data.

CONTEXT:
{context}

ROUTE QUERY:
{question}

ANALYSIS:
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

retriever = get_retriever()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Define the specific chain for this agent
mobility_rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
