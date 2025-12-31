from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI)
db = client["patient_reports_local"]
pdf_chunks_collection = db["pdf_chunks"]
