import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from ..tools.vector_store import get_retriever

# Load environment variables
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.env"))
load_dotenv(dotenv_path=dotenv_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama3-8b-8192")

# 1. Initialize the LLM
# We set temperature to 0 for more deterministic, fact-based answers.
llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name=LLM_MODEL_NAME)

# 2. Create a Prompt Template
# This template structures how we present the context and question to the LLM.
prompt_template = """
You are an expert logistics assistant for a system called LogiMAS.
Use the following retrieved context to answer the user's question.
If you don't know the answer, just say that you don't know. Be concise.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

# 3. Get the retriever from our tool
retriever = get_retriever()

# 4. Define a function to format the retrieved documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 5. Build the RAG Chain using LangChain Expression Language (LCEL)
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Example usage (for testing)
if __name__ == "__main__":
    print("Testing the RAG chain...")
    question = "    "
    
    # .invoke() runs the entire chain: retrieve -> format -> prompt -> llm -> parse
    response = rag_chain.invoke(question)
    
    print(f"\nQuestion: {question}")
    print(f"Answer: {response}")