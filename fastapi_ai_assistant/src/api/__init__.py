from fastapi import APIRouter

from api.v1 import chat_1

router = APIRouter()


router.include_router(
    chat_1.router,
    prefix="/v1/chat1",
    tags=["ChatExample"],
)
