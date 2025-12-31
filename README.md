
# RAG Medical Summary

This project is a small retrieval-augmented generation (RAG) service for summarizing and querying patient PDF reports. It uses FastAPI for the HTTP API, splits and indexes PDF content into chunks, stores chunk embeddings in MongoDB, and uses a text-generation model (Gemini via Google GenAI or a local LLM) to answer queries using retrieved context.

## Features

- Upload PDFs and chunk them into passages suitable for embedding and retrieval
- Store chunk text and embeddings in MongoDB
- Perform semantic search over stored chunks and use the top matches as context for a generative model
- Simple HTTP API (upload and query endpoints)

## Project layout

- `app/main.py` — FastAPI app with `/upload-pdf` and `/query/` endpoints
- `app/services/pdf_loader.py` — PDF loading and chunking
- `app/services/embedder.py` — embedding generation, storage, and search utilities
- `app/services/vector_store.py` — (optional) wraps a LangChain-compatible vector store (MongoDB Atlas)
- `app/models/schemas.py` — MongoDB client / collection objects
- `app/utils/config.py` — environment/configuration values

## Requirements

The repository includes a minimal `requirements.txt` with `fastapi`. The code also relies on several additional packages; install them before running the app. A recommended install set (you can tweak versions as needed):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install "uvicorn[standard]" motor pymongo sentence-transformers numpy python-multipart langchain-community langchain-text-splitters google-generative-ai
```

Notes:
- `motor` is the async MongoDB driver used by `app/models/schemas.py`.
- `sentence-transformers` provides a local embedding model used in `app/services/embedder.py`.
- `google-generative-ai` (or the appropriate GenAI client package) is used to call Gemini; confirm the package name and version for your environment.
- `python-multipart` is required by FastAPI to accept file uploads.

## Configuration (environment variables)

The app reads configuration from environment variables (and `.env` if present). Key variables used across the project:

- `GEMINI_API_KEY` — API key for Google Gemini / GenAI
- `MONGO_URI` or `MONGO_DB_URI` — MongoDB connection string (examples below)
- `DB_NAME` — database name (used by some modules)
- `COLLECTION_NAME` — collection name for storing chunks/embeddings

Example `.env` file (create at project root):

```
GEMINI_API_KEY=sk-...
MONGO_URI=mongodb://localhost:27017
DB_NAME=patient_reports_local
COLLECTION_NAME=pdf_chunks
```

On Windows PowerShell you can set variables for the current session like this:

```powershell
#$env:GEMINI_API_KEY = "your_api_key_here"
#$env:MONGO_URI = "mongodb://localhost:27017"
```

To persist an environment variable across sessions you can use `setx` (note: requires opening a new shell to take effect):

```powershell
setx GEMINI_API_KEY "your_api_key_here"
setx MONGO_URI "mongodb://localhost:27017"
```

## Running the app (development)

Start the FastAPI app with Uvicorn. From the project root (after activating your venv):

```powershell
# development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If you prefer the `uvicorn` CLI directly:

```powershell
uvicorn app.main:app --reload
```

After starting, the API will be available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

## API endpoints

- POST `/upload-pdf` — multipart form, file field named `file`. The endpoint saves the uploaded PDF to a temporary directory, chunks it, generates embeddings for chunks, and stores the results in MongoDB.

	Example (PowerShell with `curl.exe`):

	```powershell
	curl.exe -X POST "http://localhost:8000/upload-pdf" -F "file=@C:\path\to\report.pdf"
	```

- GET `/query/?q=your+question` — query the indexed PDFs. The service retrieves the top relevant chunks and asks the model to answer using that context. Example:

	```powershell
	Invoke-RestMethod -Method GET -Uri "http://localhost:8000/query/?q=what+is+the+patient+diagnosis"
	```

Responses are JSON objects containing the answer text and metadata such as how many chunks were used.

## Data flow summary

1. Upload PDF via `/upload-pdf`.
2. `app/services/pdf_loader.py` loads and splits documents into chunks.
3. `app/services/embedder.py` encodes each chunk into a numeric embedding (uses a local `sentence-transformers` model in this project) and stores the chunk text + embedding in MongoDB.
4. A user query is encoded and compared against stored embeddings to find top matching chunks; those chunks are combined into a context prompt and sent to Gemini (or another model) to generate an answer.

## MongoDB / Vector store notes

- You can run MongoDB locally or use Atlas. If you plan to use MongoDB Atlas Vector Search / the `MongoDBAtlasVectorSearch` vectorstore from LangChain, create the appropriate vector index and confirm field names match what the vector store expects (e.g., an `embedding` field with float arrays).
- The repository contains two patterns: a simple `motor` async client in `app/models/schemas.py` (used by the embedder) and `app/services/vector_store.py` which demonstrates creating a LangChain MongoDB vector store. Ensure your env variables and code paths are consistent (`MONGO_URI`, `MONGO_DB_URI`, `DB_NAME`, `COLLECTION_NAME`).

## Troubleshooting

- If uploads fail with `multipart` errors, confirm `python-multipart` is installed.
- If MongoDB connections fail, verify `MONGO_URI` / `MONGO_DB_URI` and that MongoDB is reachable from your machine.
- If embeddings or model calls fail, confirm the `GEMINI_API_KEY` is set and valid, and that the GenAI client package version matches the API used in the code.

## Next steps / improvements

- Centralize configuration keys and remove duplicate/ambiguous names in `app/utils/config.py` (choose either `MONGO_URI` or `MONGO_DB_URI` and use it consistently).
- Add logging and error handling around external calls (MongoDB, model API).
- Consider using a single module-level `MongoClient` (or `AsyncIOMotorClient`) instance reused across the process rather than creating new clients per call.
- Add unit/integration tests for chunking, embedding, and API endpoints.

## License

MIT

