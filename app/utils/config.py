import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
MONGO_DB_URI=os.getenv("MONGO_DB_URI")
DB_NAME=os.getenv("DB_NAME")
COLLECTION_NAME=os.getenv("COLLECTION_NAME")
import os
from dotenv import load_dotenv

load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
