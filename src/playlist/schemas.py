from pydantic import BaseModel


class PlaylistCreate(BaseModel):
    track: str


class VideoUrl(BaseModel):
    video_url: str
