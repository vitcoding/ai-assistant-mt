from fastapi import APIRouter

from api.v1 import chat_1, chat_2, chat_3

router = APIRouter()


router.include_router(
    chat_1.router,
    prefix="/v1/chat1",
    tags=["ChatExample"],
)

router.include_router(
    chat_2.router,
    prefix="/v1/chat2",
    tags=["ChatExample"],
)

router.include_router(
    chat_3.router,
    prefix="/v1/chat3",
    tags=["ChatExample"],
)
