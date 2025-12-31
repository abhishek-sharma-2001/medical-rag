from google import genai
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models.schemas import pdf_chunks_collection
from app.utils.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

model = SentenceTransformer("all-mpnet-base-v2")  # 768-dim embeddings

async def store_pdf_with_embeddings(file_name: str, chunks: list):
    for chunk in chunks:
        # Generate embedding using local model
        embedding_array = model.encode(chunk.page_content, convert_to_numpy=True)

        # Convert numpy array to list
        embedding_list = embedding_array.tolist()

        # Prepare document for MongoDB
        doc = {
            "file_name": file_name,
            "text": chunk.page_content,
            "embedding": embedding_list
        }

        # Insert into MongoDB
        await pdf_chunks_collection.insert_one(doc)


import numpy as np

async def search_pdf(query: str, top_k=10):
    # Query embedding
    query_emb = model.encode(query, convert_to_numpy=True).tolist()

    # Fetch all chunks from MongoDB
    cursor = pdf_chunks_collection.find({})
    results = []

    async for doc in cursor:
        emb = doc["embedding"]  # Already a list of floats
        # Cosine similarity
        sim = np.dot(emb, query_emb) / (np.linalg.norm(emb) * np.linalg.norm(query_emb))
        results.append((sim, doc))

    # Sort by similarity
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1]["text"] for r in results[:top_k]]


async def summarize_text(texts: list[str]):
    combined_text = "\n".join(texts)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Summarize the following pdf:\n{combined_text}"
    )
    return response.text
