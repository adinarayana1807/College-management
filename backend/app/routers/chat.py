"""Chat router - accepts a question and returns an answer using the RAG skeleton."""
from typing import Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rag import get_answer

router = APIRouter()

class Query(BaseModel):
    question: str


@router.post('/query')
async def query(q: Query):
    if not q.question:
        raise HTTPException(status_code=400, detail="Question is required")
    answer = await get_answer(q.question)
    return answer
