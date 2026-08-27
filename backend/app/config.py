import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = BASE_DIR / 'backend'
SAMPLE_DATA_DIR = BACKEND_DIR / 'sample_data'
VECTOR_DB_DIR = BACKEND_DIR / 'vector_db'
DB_DIR = BACKEND_DIR / 'database'

# Create directories if they don't exist
VECTOR_DB_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DB_DIR}/college_rag.db"

# Vector Store
CHROMA_PERSIST_DIR = str(VECTOR_DB_DIR / 'chroma_db')

# LLM Configuration
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# JWT
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# CORS
ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
]

# Chunking parameters
CHUNK_SIZE = 600
CHUNK_OVERLAP = 120

# Vector search
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.3
