from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import ALLOWED_ORIGINS, BASE_DIR

app = FastAPI(
    title='Apex College AI',
    description='RAG-based College Management System',
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
    app.mount('/frontend', StaticFiles(directory=frontend_dir), name='frontend')

# Mount root static files (index.html, style.css, etc.)
app.mount('/static', StaticFiles(directory=BASE_DIR), name='static')

# Include routers (to be implemented)
# from app.routers import auth, chat, documents, admin
# app.include_router(auth.router, prefix='/api/auth', tags=['Auth'])
# app.include_router(chat.router, prefix='/api/chat', tags=['Chat'])
# app.include_router(documents.router, prefix='/api/documents', tags=['Documents'])
# app.include_router(admin.router, prefix='/api/admin', tags=['Admin'])

@app.get('/')
async def root():
    return {'message': 'Apex College AI is running'}

@app.get('/health')
async def health():
    return {'status': 'healthy'}
