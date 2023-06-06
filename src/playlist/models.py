from sqlalchemy import Column, Integer, String

from src.database import Base


class Playlist(Base):
    __tablename__ = 'playlist'

    id = Column(Integer, primary_key=True)
    track = Column(String)
