from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship, validates

from dblit.base import Base
from dblit.label_set_item import LabelSetItem
from dblit.label_job import LabelJob


class LabelJobItem(Base):
    __tablename__ = 'label_job_item'

    id = Column(Integer, primary_key=True)

    label_job_id = Column(Integer, ForeignKey('label_job.id'), nullable=False)
    label_job = relationship("LabelJob", backref="label_job_items")

    label_set_item_id = Column(Integer, ForeignKey('label_set_item.id'), nullable=False)
    label_set_item = relationship("LabelSetItem")  # no backref!

    override_label_id = Column(Integer, ForeignKey('label.id'))
    override_label = relationship("Label")  # no backref!

    def __init__(self, label_job: LabelJob, label_set_item: LabelSetItem):
        self.label_job = label_job
        self.label_set_item = label_set_item

    @validates('label_set_item')
    def validate_label_set_item(self, key, label_set_item: LabelSetItem):
        assert self.label_job.label_set.code == label_set_item.label.label_set.code
        return label_set_item
