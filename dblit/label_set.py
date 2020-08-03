from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import validates

from dblit.base import Base


class LabelSet(Base):
    __tablename__ = 'label_set'

    id = Column(Integer, primary_key=True)
    code: str = Column(String, nullable=False, unique=True)

    def __init__(self, code: str):
        self.code = code

    @validates('code')
    def validate_code(self, key, code: str):
        assert code is not None and len(code) > 0
        return code
