from pydantic import BaseModel


class PlaylistCreate(BaseModel):
    track: str
    length: int


class VideoUrl(BaseModel):
    video_url: str
