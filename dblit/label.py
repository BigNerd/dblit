from sqlalchemy import Column, ForeignKey, String, Integer, UniqueConstraint
from sqlalchemy.orm import relationship, validates

from dblit.base import Base


class Label(Base):
    __tablename__ = 'label'

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)

    label_set_id = Column(Integer, ForeignKey('label_set.id'), nullable=False)
    label_set = relationship("LabelSet", backref="labels")

    __table_args__ = (
        UniqueConstraint('code', 'label_set_id'),
        UniqueConstraint('name', 'label_set_id'),
    )

    def __init__(self, code: str, name: str, label_set):
        self.code = code
        self.name = name
        self.label_set = label_set

    @validates('code')
    def validate_code(self, key, code: str):
        assert code is not None and len(code) > 0
        return code

    @validates('name')
    def validate_code(self, key, name: str):
        assert name is not None and len(name) > 0
        return name
