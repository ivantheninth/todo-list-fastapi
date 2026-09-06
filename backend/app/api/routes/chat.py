from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import get_current_user
from app.db.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import llm_service


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
        user_request: ChatRequest,
        current_user: User = Depends(get_current_user),
):
    try:
        return await llm_service.ask(user_request.message)

    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="LLM service is temporarily unavailable",
        )