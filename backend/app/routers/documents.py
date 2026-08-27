"""Documents router - upload and index documents (skeleton).
Saves uploaded files to SAMPLE_DATA_DIR and exposes endpoints to index documents
into a local FAISS vector store.
"""
import os
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import aiofiles

from app.config import SAMPLE_DATA_DIR
from app.services.vector_store import index_all_documents, index_exists

router = APIRouter()


@router.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = SAMPLE_DATA_DIR / file.filename
    try:
        async with aiofiles.open(dest, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    return {"filename": file.filename, "path": str(dest)}


@router.post('/index')
async def index_documents():
    """Index all files found in SAMPLE_DATA_DIR into the vector store."""
    SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    n = index_all_documents()
    return {"indexed_documents": n}


@router.get('/status')
async def index_status():
    return {"index_exists": index_exists()}
