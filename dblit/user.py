from sqlalchemy import Column, String, Integer

from dblit.base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name
