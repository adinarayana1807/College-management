import re
from pathlib import Path
from typing import List
from app.config import SAMPLE_DATA_DIR, VECTOR_DB_DIR
import joblib
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Simple vector store using TF-IDF and joblib persistence.
# This keeps the RAG pipeline local and avoids depending on external vector DB services.

class SimpleVectorStore:
    def __init__(self, persist_dir: Path):
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.persist_dir / 'vector_index.pkl'
        self.docs = []  # list of dicts: {id, text, source, meta}
        self.vectorizer = None
        self.embeddings = None
        self._load()

    def _load(self):
        if self.index_path.exists():
            data = joblib.load(self.index_path)
            self.docs = data.get('docs', [])
            self.vectorizer = data.get('vectorizer')
            self.embeddings = data.get('embeddings')

    def _save(self):
        joblib.dump({'docs': self.docs, 'vectorizer': self.vectorizer, 'embeddings': self.embeddings}, self.index_path)

    def add_documents(self, docs: List[dict]):
        # docs: [{'id','text','source','meta'}]
        self.docs.extend(docs)
        texts = [d['text'] for d in self.docs]
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=20000)
        self.embeddings = self.vectorizer.fit_transform(texts)
        self._save()

    def query(self, query_text: str, top_k: int = 5):
        if not self.docs or self.vectorizer is None:
            return []
        q_vec = self.vectorizer.transform([query_text])
        sims = cosine_similarity(q_vec, self.embeddings)[0]
        ranked_idx = sims.argsort()[::-1][:top_k]
        results = []
        for idx in ranked_idx:
            results.append({'id': self.docs[idx]['id'], 'text': self.docs[idx]['text'], 'source': self.docs[idx]['source'], 'meta': self.docs[idx].get('meta'), 'score': float(sims[idx])})
        return results

# Utilities: extract text and chunking

def extract_text_from_file(path: Path) -> str:
    path = Path(path)
    suffix = path.suffix.lower()
    text = ''
    try:
        if suffix == '.pdf':
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            pages = [p.extract_text() or '' for p in reader.pages]
            text = "\n".join(pages)
        elif suffix in ('.docx', '.doc'):
            from docx import Document
            doc = Document(str(path))
            paras = [p.text for p in doc.paragraphs]
            text = "\n".join(paras)
        else:
            # try plain text
            text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        text = ''
    # basic cleanup
    text = re.sub(r"\s+"," ", text).strip()
    return text


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 120) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start = end - overlap
    return chunks


def format_context_for_prompt(results: List[dict]) -> str:
    parts = []
    for r in results:
        parts.append(f"[source: {r['source']} | score: {r.get('score',0):.3f}]\n{r['text']}")
    return "\n\n---\n\n".join(parts)


# Initialize a global vector store instance
vector_store = SimpleVectorStore(persist_dir=VECTOR_DB_DIR)
