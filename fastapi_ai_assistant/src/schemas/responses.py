from pydantic import BaseModel


class AudioUploadResponse(BaseModel):
    filename: str
