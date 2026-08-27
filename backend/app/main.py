from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import ALLOWED_ORIGINS, BASE_DIR

# Import routers
from app.routers import auth, chat, documents

app = FastAPI(
    title='Apex College AI',
    description='RAG-based College Management System (skeleton)',
    version='1.0.0'
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Mount frontend static files
frontend_dir = BASE_DIR / 'frontend'
if frontend_dir.exists():
    app.mount('/frontend', StaticFiles(directory=str(frontend_dir)), name='frontend')

# Serve frontend as /static for compatibility with the original project
static_dir = frontend_dir
if static_dir.exists():
    app.mount('/static', StaticFiles(directory=str(static_dir)), name='static')

# Include routers
app.include_router(auth.router, prefix='/api/auth', tags=['Auth'])
app.include_router(chat.router, prefix='/api/chat', tags=['Chat'])
app.include_router(documents.router, prefix='/api/documents', tags=['Documents'])


@app.get('/')
async def root():
    return {'message': 'Apex College AI is running (RAG skeleton branch)'}


@app.get('/health')
async def health():
    return {'status': 'healthy'}
