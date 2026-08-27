"""Simple FAISS-backed vector store with persistence for the skeleton.
Stores index at VECTOR_DB_DIR/faiss.index and metadata at VECTOR_DB_DIR/metadata.pkl
"""
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

from app.config import VECTOR_DB_DIR, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS
from app.services.embeddings import EmbeddingsProvider
from app.services.extractor import extract_text_from_pdf
from app.services.chunker import chunk_text

VECTOR_DB_DIR = Path(VECTOR_DB_DIR)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
INDEX_PATH = VECTOR_DB_DIR / 'faiss.index'
META_PATH = VECTOR_DB_DIR / 'metadata.pkl'

try:
    import faiss
except Exception:
    faiss = None


def index_exists() -> bool:
    return INDEX_PATH.exists() and META_PATH.exists()


def _load_metadata():
    if META_PATH.exists():
        with open(META_PATH, 'rb') as f:
            return pickle.load(f)
    return []


def _save_metadata(meta):
    with open(META_PATH, 'wb') as f:
        pickle.dump(meta, f)


def index_all_documents() -> int:
    """Scan SAMPLE_DATA_DIR, extract text, chunk, embed and save FAISS index."""
    from app.config import SAMPLE_DATA_DIR
    SAMPLE_DATA_DIR = Path(SAMPLE_DATA_DIR)
    files = list(SAMPLE_DATA_DIR.glob('*'))
    docs = []
    for f in files:
        if f.is_file():
            text = extract_text_from_pdf(f)
            if not text:
                # fallback: read raw text
                try:
                    text = f.read_text(errors='ignore')
                except Exception:
                    text = ''
            chunks = chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
            for i, c in enumerate(chunks):
                docs.append({'id': f"{f.name}::{i}", 'text': c, 'source': str(f.name)})

    if not docs:
        return 0

    texts = [d['text'] for d in docs]
    emb = EmbeddingsProvider().embed_texts(texts)
    arr = np.array(emb).astype('float32')

    if faiss is None:
        raise RuntimeError('faiss-cpu is required for the vector store')

    dim = arr.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(arr)
    faiss.write_index(index, str(INDEX_PATH))
    meta = docs
    _save_metadata(meta)
    return len(docs)


def search(query: str, top_k: int = TOP_K_RESULTS) -> List[Dict[str, Any]]:
    if not index_exists():
        return []
    emb = EmbeddingsProvider().embed_texts([query])
    arr = np.array(emb).astype('float32')
    index = faiss.read_index(str(INDEX_PATH))
    D, I = index.search(arr, top_k)
    meta = _load_metadata()
    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx < 0 or idx >= len(meta):
            continue
        item = meta[idx]
        results.append({'id': item['id'], 'text': item['text'], 'source': item.get('source'), 'score': float(dist)})
    return results
