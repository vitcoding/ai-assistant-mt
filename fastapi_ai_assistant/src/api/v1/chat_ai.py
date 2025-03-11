from datetime import datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)

from core.config import templates
from core.logger import log
from services.chat_ai import ChatAI
from services.websocket_connection import manager

router = APIRouter()


# url: http://localhost:8005/api/v1/chat_ai/
@router.get("/")
async def get(request: Request):
    log.debug(f"{__name__}: {get.__name__}: run")
    return templates.TemplateResponse(request, "chat_ai.html")


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    log.debug(f"{__name__}: {get_cookie_or_token.__name__}: run")
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@router.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    item_id: str,
    q: int | None = None,
    cookie_or_token: Annotated[str, Depends(get_cookie_or_token)],
    use_rag: Annotated[bool, Query()],
):
    log.debug(f"{__name__}: {websocket_endpoint.__name__}: run")

    await manager.connect(websocket)
    chat = ChatAI(item_id, websocket)

    await chat.send_message("System", f"Использование RAG '{use_rag}'.")

    try:
        while True:
            user_message = await websocket.receive_text()

            await chat.send_message(chat.user_role_name, user_message)

            ai_message_timestamp = datetime.now().isoformat()
            await websocket.send_text(
                f"[{ai_message_timestamp}] {chat.ai_role_name}: \n"
            )
            async for chunk in chat.process(user_message, use_rag):
                await websocket.send_text(chunk)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
