"""RAG orchestration (skeleton).
Performs a vector search and builds a simple answer using the retrieved context.
If an LLM API key is provided and configured, it can call the LLM to produce a
final answer — otherwise returns a synthetic answer based on the retrieved texts.
"""
import os
from typing import Dict, Any

from app.services.vector_store import search, index_exists

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'local')


async def get_answer(question: str) -> Dict[str, Any]:
    # If no index exists, return helpful fallback
    if not index_exists():
        return {
            'answer': "I couldn't find any indexed college documents. Please upload and index documents first.",
            'sources': [],
            'confidence': 0.0,
        }

    results = search(question)
    if not results:
        return {
            'answer': "I couldn't find relevant information in the indexed documents.",
            'sources': [],
            'confidence': 0.0,
        }

    # Build a simple combined context
    combined = "\n---\n".join([f"Source: {r['source']}\n{r['text']}" for r in results])

    # If OpenAI is configured and user set LLM_PROVIDER=openai, call it (optional)
    if LLM_PROVIDER == 'openai' and OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            prompt = f"Use the following context to answer the question. Context:\n{combined}\nQuestion: {question}\nAnswer:"
            resp = openai.ChatCompletion.create(model='gpt-4o-mini', messages=[{'role':'user','content':prompt}], max_tokens=512)
            text = resp['choices'][0]['message']['content']
            return {'answer': text, 'sources': [r['source'] for r in results], 'confidence': 0.8}
        except Exception:
            # fallback to local reply
            pass

    # Local/skeleton answer: return combined context as the 'answer' with sources
    snippet = combined[:1500]
    answer = f"I found the following passages that may help:\n{snippet}"
    return {'answer': answer, 'sources': [r['source'] for r in results], 'confidence': 0.5}
