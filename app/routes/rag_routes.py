import tempfile
from fastapi import FastAPI
from pydantic import BaseModel
import shutil

from app.services.pdf_loader import load_and_chunk_pdfs
from app.services.rag_chain import query_rag, store_documents

class UploadFile(BaseModel):
    filename: str
    content: bytes

router = FastAPI()

@router.post("/upload")
async def upload_pdfs(files: list[UploadFile]):
    paths = []
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            shutil.copyfileobj(file.file, tmp)
            paths.append(tmp.name)

    docs = load_and_chunk_pdfs(paths)
    response = store_documents(docs)
    return response

@router.get("/query")
async def query_patient_data(q: str):
    result = query_rag(q)
    return {"answer": result}