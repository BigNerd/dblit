from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship

from dblit.base import Base
from dblit.label_set import LabelSet


class Label(Base):
    __tablename__ = 'label'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)

    label_set_id = Column(Integer, ForeignKey('label_set.id'))
    label_set = relationship("LabelSet", back_populates="labels")

    def __init__(self, code: str, name: str, label_set):
        self.code = code
        self.name = name
        self.label_set = label_set


LabelSet.labels = relationship("Label", order_by=Label.id, back_populates="label_set")
