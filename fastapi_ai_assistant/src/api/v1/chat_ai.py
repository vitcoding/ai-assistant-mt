from datetime import datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Query,
    WebSocket,
    WebSocketException,
    status,
)
from fastapi.responses import HTMLResponse

from services.chat_ai import ChatAI
from core.logger import log

router = APIRouter()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                var itemId = document.getElementById("itemId")
                var token = document.getElementById("token")
                ws = new WebSocket("ws://localhost:8005/api/v1/chat_ai/items/" + itemId.value + "/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault()
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


# url: http://localhost:8005/api/v1/chat_ai/
@router.get("/")
async def get():
    log.info(f"{__name__}: {get.__name__}: run")
    return HTMLResponse(html)


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    log.info(f"{__name__}: {get_cookie_or_token.__name__}: run")
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
):
    log.info(f"{__name__}: {websocket_endpoint.__name__}: run")
    await websocket.accept()
    chat = ChatAI(item_id)
    while True:
        user_message = await websocket.receive_text()
        user_message_timestamp = datetime.now().isoformat()
        await websocket.send_text(
            f"[{user_message_timestamp}] Я: {user_message}"
        )
        ai_message = await chat.process(user_message)
        ai_message_timestamp = datetime.now().isoformat()
        await websocket.send_text(f"[{ai_message_timestamp}] ИИ: {ai_message}")
