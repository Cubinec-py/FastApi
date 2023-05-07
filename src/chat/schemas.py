from pydantic import BaseModel


class MessageModel(BaseModel):
    id: int
    message: str

    class Config:
        orm_mode = True
