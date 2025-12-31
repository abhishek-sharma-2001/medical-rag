from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Your local service imports
from app.services.embedder import get_gemini_embeddings
from app.services.vector_store import get_vector_store
from app.utils.config import GEMINI_API_KEY


def store_documents(docs):
    """Store documents in the FAISS vector store."""
    vector_store = get_vector_store()
    embeddings = get_gemini_embeddings()
    vector_store.add_documents(docs, embedding=embeddings)
    vector_store.persist()
    print(f"✅ Stored {len(docs)} documents in the vector store.")
    return vector_store


def query_rag(question: str):
    """Query the RAG system using Gemini."""
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        google_api_key=GEMINI_API_KEY
    )

    prompt = ChatPromptTemplate.from_template(
        """You are a helpful medical assistant. Use the context below to answer the question.

        Context:
        {context}

        Question: {input}

        Answer:"""
    )

    # Create RAG chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    result = rag_chain.invoke({"input": question})
    return result["answer"]
