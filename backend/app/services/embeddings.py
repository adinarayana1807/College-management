"""Embeddings provider wrapper.
Defaults to a local sentence-transformers model if OPENAI is not configured.
"""
import os
from typing import List

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'local')

# Local model
_local_model = None


def _init_local_model():
    global _local_model
    if _local_model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except Exception:
            raise RuntimeError("sentence-transformers is required for local embeddings")
        _local_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _local_model


class EmbeddingsProvider:
    def __init__(self):
        self.provider = LLM_PROVIDER
        if self.provider == 'local':
            _init_local_model()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if self.provider == 'openai' and OPENAI_API_KEY:
            # Lazy import to avoid requiring openai if not used
            try:
                import openai
            except Exception:
                raise RuntimeError('openai package required for OpenAI embeddings')
            openai.api_key = OPENAI_API_KEY
            res = openai.Embedding.create(model='text-embedding-3-small', input=texts)
            return [r['embedding'] for r in res['data']]
        else:
            model = _init_local_model()
            embeddings = model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()
