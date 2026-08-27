from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
import shutil
from pathlib import Path
from typing import List

from app.config import SAMPLE_DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from app.services.rag import vector_store, extract_text_from_file, chunk_text

router = APIRouter()

# Ensure sample data dir exists
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

@router.post('/upload', summary='Upload document and add to vector store')
async def upload_document(file: UploadFile = File(...)):
    try:
        file_id = str(uuid4())
        dest_path = SAMPLE_DATA_DIR / f"{file_id}_{file.filename}"
        with dest_path.open('wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = extract_text_from_file(dest_path)
        if not text:
            raise HTTPException(status_code=400, detail='No text could be extracted from the file')

        chunks = chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        docs = []
        for idx, c in enumerate(chunks):
            docs.append({'id': f"{file_id}_{idx}", 'text': c, 'source': str(dest_path), 'meta': {'filename': file.filename, 'chunk': idx}})

        vector_store.add_documents(docs)
        return JSONResponse({'status': 'ok', 'added_chunks': len(docs), 'file': file.filename})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/list', summary='List indexed documents')
async def list_documents():
    return {'count': len(vector_store.docs), 'documents': [{'id': d['id'], 'source': d['source'], 'meta': d.get('meta')} for d in vector_store.docs]}
