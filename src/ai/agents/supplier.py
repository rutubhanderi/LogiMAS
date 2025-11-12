from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from ..tools.vector_store import get_retriever  # Relative import remains the same
from .shared import llm  # Relative import remains the same

# A prompt specifically for supplier-related queries
prompt_template = """
You are a supplier management assistant for LogiMAS.
Your role is to answer questions about supplier contracts, lead times, and regions based on the provided context.
If the context does not contain the answer, state that the information is not available in the knowledge base.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

retriever = get_retriever()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Define the specific chain for this agent
supplier_rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
