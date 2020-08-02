from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dblit.base import Base
from dblit.label import Label


class LabelSetItem(Base):
    __tablename__ = 'label_set_item'

    id = Column(Integer, primary_key=True)
    uri = Column(String)

    label_id = Column(Integer, ForeignKey('label.id'))
    label: Label = relationship("Label")

    def __init__(self, uri: str, label: Label):
        self.uri = uri
        self.label: Label = label
