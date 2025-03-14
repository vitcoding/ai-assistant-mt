import os
from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Path,
    Query,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse

from core.config import templates
from core.logger import log
from services.audio.speech_to_text import SpeechToText
from services.chat_ai import ChatAI
from services.llm_languages import LANGUAGES, get_langage_by_index
from services.llm_models import MODELS, get_model_by_index
from services.tools.message_template import (
    get_chat_start_message,
    get_message_header,
)
from services.tools.path_identifier import PathCreator
from services.tools.time_stamp import TimeStamp
from services.websocket_connection import manager

router = APIRouter()


# url: http://localhost:8005/api/v1/chat_ai/
@router.get("/")
async def get(request: Request):
    log.debug(f"{__name__}: {get.__name__}: run")

    ###
    user_id = "noname"
    timestamp = TimeStamp()
    path_creator = PathCreator(timestamp, user_id)
    item_id = path_creator.get_url()

    previous_chat_history = False

    return templates.TemplateResponse(
        request,
        "chat_ai.html",
        context={
            "item_id": item_id,
            "models": MODELS,
            "languages": LANGUAGES,
            "previous_chat": previous_chat_history,
        },
    )


@router.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    item_id: str,
    q: int | None = None,
    chat_topic: Annotated[str, Query()],
    model_index: Annotated[int, Query()],
    language_index: Annotated[int, Query()],
    use_rag: Annotated[bool, Query()],
    use_sound: Annotated[bool, Query()],
):
    log.debug(f"{__name__}: {websocket_endpoint.__name__}: run")

    model_name = get_model_by_index(model_index - 1)
    language = get_langage_by_index(language_index - 1)
    await manager.connect(websocket)

    chat = ChatAI(
        websocket,
        item_id,
        chat_topic,
        model_name,
        language,
        use_rag,
        use_sound,
    )
    stt = SpeechToText()

    SHOW_START_MESSAGE = False
    if SHOW_START_MESSAGE:
        start_message = get_chat_start_message(chat.language, chat.chat_id)
        await chat.send_message(start_message)

    try:
        while True:
            user_message = await websocket.receive_text()

            # audio input
            if user_message == "<<<audio>>>":
                user_message = await stt.transcribe_audio()

            await chat.send_message(user_message, chat.user_role_name)

            message_header = get_message_header(
                chat.language, chat.ai_role_name
            )
            await websocket.send_text(f"{message_header} \n")
            async for chunk in chat.process(user_message):
                await websocket.send_text(chunk)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/upload-audio")
async def upload_audio(uploaded_audio: UploadFile = File(...)):

    with open(f"{uploaded_audio.filename}", "wb") as buffer:
        while contents := uploaded_audio.file.read(1024 * 16):
            buffer.write(contents)

    return {"filename": uploaded_audio.filename}


@router.get("/wav/{file_id}")
async def get_wav(file_id: str = Path(...)):

    log.info(f"file_id: {file_id}")
    filename = f"{file_id}.wav"

    if not os.path.exists(filename):
        raise HTTPException(
            status_code=404, detail=f"File {filename} not found"
        )

    return FileResponse(
        path=filename,
        media_type="audio/wav",
        headers={"Content-Disposition": f"attachment; filename={file_id}.wav"},
    )
