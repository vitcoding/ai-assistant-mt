import os
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    Query,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import FileResponse

from core.config import config, templates
from core.logger import log
from secure import api_key_schema
from secure.auth import UpgradeAPIKeyCookie
from services.audio.speech_to_text import SpeechToText
from services.cache import CacheService, get_cache_service
from services.chat_ai import ChatAI
from services.llm_languages import LANGUAGES, get_langage_by_index
from services.llm_models import MODELS, get_model_by_index
from services.tools.message_template import (
    get_chat_start_message,
    get_message_header,
)
from services.tools.path_identifier import PathCreator
from services.tools.path_manager import PathManager
from services.tools.time_stamp import TimeStamp
from services.websocket_connection import manager

router = APIRouter()


# url: http://localhost:8005/api/v1/chat_ai/
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="AI Chat",
    description="Start a chat with AI",
    response_description="A chat AI template html",
)
async def get(
    request: Request,
    auth: str = Depends(api_key_schema),
):
    log.debug(f"{__name__}: {get.__name__}: run")

    user_id = UpgradeAPIKeyCookie.get_current_user(auth[0])

    timestamp = TimeStamp()
    path_creator = PathCreator(timestamp, user_id)
    chat_id = path_creator.get_url()

    previous_chat_history = False

    return templates.TemplateResponse(
        request,
        "chat_ai.html",
        context={
            "service_host": config.globals.ai_service_host,
            "chat_id": chat_id,
            "models": MODELS,
            "languages": LANGUAGES,
            "previous_chat": previous_chat_history,
        },
    )


@router.websocket("/{chat_id}/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    chat_id: str,
    chat_topic: Annotated[str, Query()],
    model_index: Annotated[int, Query()],
    language_index: Annotated[int, Query()],
    use_rag: Annotated[bool, Query()],
    use_sound: Annotated[bool, Query()],
    cache: CacheService = Depends(get_cache_service),
):
    log.debug(f"{__name__}: {websocket_endpoint.__name__}: run")

    model_name = get_model_by_index(model_index - 1)
    language = get_langage_by_index(language_index - 1)
    await manager.connect(websocket)

    path_manager = PathManager()
    path_manager.set_chat_directories(chat_id)

    chat = ChatAI(
        websocket,
        chat_id,
        chat_topic,
        model_name,
        language,
        use_rag,
        use_sound,
        path_manager,
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
                file_path_b = await cache.get(
                    f"chat_id: {chat.chat_id}: user_audio"
                )
                file_path = file_path_b.decode("utf-8")
                user_message = await stt.transcribe_audio(file_path)

            await chat.send_message(user_message, chat.user_role_name)

            message_header, ai_file_name = get_message_header(
                chat.language, chat.ai_role_name
            )
            if chat.use_sound:
                chat.ai_audio_file_name = ai_file_name
            await websocket.send_text(f"{message_header} \n")
            async for chunk in chat.process(user_message, ai_file_name):
                await websocket.send_text(chunk)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post(
    "/upload-audio",
    status_code=status.HTTP_200_OK,
    summary="Upload audio",
    description="Upload an audio file of a message",
    response_description="A name of an audio file",
)
async def upload_audio(
    uploaded_audio: UploadFile = File(...),
    cache: CacheService = Depends(get_cache_service),
) -> dict[str, str]:
    audio_file_name = uploaded_audio.filename

    path_manager = PathManager()
    file_name = path_manager.parse_audio_message_filename(audio_file_name)
    save_directory = path_manager.chat_dir_audio
    file_path = f"{save_directory}{file_name}.wav"

    chat_id = path_manager.chat_id
    await cache.set(f"chat_id: {chat_id}: user_audio", file_path)

    with open(file_path, "wb") as buffer:
        while contents := uploaded_audio.file.read(1024 * 16):
            buffer.write(contents)

    return {"filename": file_name}


@router.get(
    "/wav/{file_id}",
    status_code=status.HTTP_200_OK,
    summary="Send audio",
    description="Send an audio file of an ai message",
    response_description="A name of an audio file",
)
async def get_wav(file_id: str = Path(...)) -> FileResponse:

    log.info(f"file_id: {file_id}")
    user_id, chat_time, file_name = file_id.split("_")
    path_manager = PathManager()
    path_manager.set_chat_directories(f"{user_id}_{chat_time}")
    filename = f"{path_manager.chat_dir_audio}{file_name}.wav"

    if not os.path.exists(filename):
        raise HTTPException(
            status_code=404, detail=f"File {filename} not found"
        )

    return FileResponse(
        path=filename,
        media_type="audio/wav",
        headers={"Content-Disposition": f"attachment; filename={file_id}.wav"},
    )
