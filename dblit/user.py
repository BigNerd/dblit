from sqlalchemy import Column, String, Integer

from dblit.base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)

    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name
