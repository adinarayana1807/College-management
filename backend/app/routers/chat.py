from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.rag import vector_store, format_context_for_prompt
from app.config import TOP_K_RESULTS
from app.config import OPENAI_API_KEY

import os

router = APIRouter()

class Question(BaseModel):
    question: str

@router.post('/ask')
async def ask(q: Question):
    if not q.question:
        raise HTTPException(status_code=400, detail='Question is required')

    results = vector_store.query(q.question, top_k=TOP_K_RESULTS)
    context = format_context_for_prompt(results)

    # If OpenAI key present, call OpenAI ChatCompletion
    if OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            system_prompt = "You are a helpful assistant. Answer using ONLY the provided context. If you don't know the answer, say you don't know. Cite sources."
            user_prompt = f"Context:\n{context}\n---\nQuestion: {q.question}\nAnswer concisely and cite sources."
            resp = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{'role':'system','content':system_prompt},{'role':'user','content':user_prompt}],
                max_tokens=512,
            )
            answer = resp.choices[0].message.content
        except Exception as e:
            # Fall back to a basic synthesized answer
            answer = "\n".join([r['text'] for r in results[:3]])
    else:
        # No LLM configured — synthesize conservative answer from found context
        if not results:
            return {'answer': "I don't have information about that yet.", 'sources': []}
        answer = "\n\n".join([r['text'] for r in results[:3]])

    sources = [{'source': r['source'], 'score': r['score']} for r in results[:TOP_K_RESULTS]]
    return {'answer': answer, 'sources': sources}
