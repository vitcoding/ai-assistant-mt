from fastapi import APIRouter

from api.v1 import chat_1, chat_2, chat_3

router = APIRouter()


# url: http://localhost:8005/api/v1/chat1/
router.include_router(
    chat_1.router,
    prefix="/v1/chat1",
    tags=["ChatExample"],
)

# url: http://localhost:8005/api/v1/chat2/
router.include_router(
    chat_2.router,
    prefix="/v1/chat2",
    tags=["ChatExample"],
)

# url: http://localhost:8005/api/v1/chat3/
router.include_router(
    chat_3.router,
    prefix="/v1/chat3",
    tags=["ChatExample"],
)
