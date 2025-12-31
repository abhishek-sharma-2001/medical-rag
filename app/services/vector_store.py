from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from app.utils.config import MONGO_DB_URI , DB_NAME, COLLECTION_NAME
from app.services.embedder import get_gemini_embeddings

# reuse a single MongoClient for the process
_client = MongoClient(MONGO_DB_URI)

def get_vector_store():
    db = _client[DB_NAME]
    collection = db[COLLECTION_NAME]
    embeddings = get_gemini_embeddings()
    store = MongoDBAtlasVectorSearch(
        collection=collection,
        embeddings=embeddings
    )
    return store