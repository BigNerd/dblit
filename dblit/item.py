from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, validates

from typing import Optional

from dblit.base import Base
from dblit.job import Job
from dblit.label import Label


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)

    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    job: Job = relationship("Job", backref="items")

    uri = Column(String, nullable=False)

    override_label_id = Column(Integer, ForeignKey('label.id'), nullable=True)
    override_label: Optional[Label] = relationship("Label")  # no backref!

    def __init__(self, job: Job, uri: str):
        self.job = job
        self.uri = uri

    @validates('uri')
    def validate_uri(self, key, uri: str):
        assert uri is not None and len(uri) > 0
        return uri

    @validates('override_label')
    def validate_override_label(self, key, override_label: Optional[Label]):
        assert override_label is None or override_label.label_set == self.job.label_set
        return override_label
