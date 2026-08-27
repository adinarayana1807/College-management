# Apex College AI — RAG-based college information assistant (skeleton)

This branch provides a lightweight RAG skeleton so you can upload documents, index them into a local FAISS vector store, and run a basic retrieval flow.

Quick start (local):

1. Create a virtual environment and install backend dependencies:

   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt

2. Copy .env example and adjust values:

   cp .env.example .env

3. Run the backend (from the repository root):

   uvicorn backend.app.main:app --reload --port 8000

4. Upload and index documents (PDFs) via the API:

   POST /api/documents/upload (multipart/form-data, file field: file)
   POST /api/documents/index

5. Query the chat endpoint:

   POST /api/chat/query  -> {"question": "What are the admission criteria?"}

Notes
- The skeleton uses a local sentence-transformers model (all-MiniLM-L6-v2) for embeddings by default. This requires internet to download the model once.
- FAISS is used for a lightweight local vector store. For production consider Chroma, Milvus, or a managed vector DB.
- If you want LLM-generated final answers, set LLM_PROVIDER=openai and provide OPENAI_API_KEY in .env — the code will try to call OpenAI (and fall back to the local combined-context reply if API fails).

Security
- This branch contains skeleton auth that accepts any username/password and returns a JWT. Replace with a proper user store and hashed-password checks before production.
