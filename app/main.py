import tempfile

from fastapi import FastAPI, UploadFile, File
import shutil

from app.services.embedder import search_pdf, summarize_text, store_pdf_with_embeddings
from app.services.pdf_loader import load_and_chunk_pdfs
from google import genai

from app.utils.config import GEMINI_API_KEY

app = FastAPI(title="Patient PDF Summarizer")
client = genai.Client(api_key=GEMINI_API_KEY)

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Use a valid temp directory
    temp_dir = tempfile.gettempdir()  # e.g., C:\Users\91981\AppData\Local\Temp
    path = f"{temp_dir}/{file.filename}"

    # Save uploaded file
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Load and chunk PDF
    chunks = load_and_chunk_pdfs([path])

    # Store chunks with embeddings
    await store_pdf_with_embeddings(file.filename, chunks)

    return {"status": "uploaded", "chunks": len(chunks)}


@app.get("/query/")
async def query_pdf(q: str):
    # 1. Retrieve top relevant chunks
    top_chunks = await search_pdf(q)

    # 2. Combine chunks for context
    context = "\n\n".join(top_chunks)

    # 3. Ask the model to answer the user's question using that context
    prompt = f"""
    You are a helpful assistant. Use the following document context to answer the question accurately.

    Document Context:
    {context}

    Question: {q}

    Answer:
    """

    # Call the model (Gemini or local LLM)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {"query": q, "answer": response.text, "chunks_used": len(top_chunks)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
