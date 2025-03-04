from fastapi import APIRouter

from api.v1 import chat_ai

router = APIRouter()

router.include_router(
    chat_ai.router,
    prefix="/v1/chat_ai",
    tags=["ChatAssistantAI"],
)
