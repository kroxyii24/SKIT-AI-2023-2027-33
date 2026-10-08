import uuid
from pydantic import BaseModel, Field


class VideoUploadRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    video_url: str  # pre-uploaded to object storage; this registers metadata
    language: str = "en"
    category: str


class VideoOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    video_url: str
    language: str
    category: str
    is_approved: bool
    view_count: int

    class Config:
        from_attributes = True
