from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates

from dblit.base import Base
from dblit.user import User
from dblit.label_set import LabelSet


class LabelJob(Base):
    __tablename__ = 'label_job'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="label_jobs")

    label_set_id = Column(Integer, ForeignKey('label_set.id'))
    label_set: LabelSet = relationship("LabelSet")

    current_label_job_item_number = Column(Integer, default=0)

    def __init__(self, user: User, label_set: LabelSet):
        self.user = user
        self.label_set = label_set

    @validates('current_label_job_item_number')
    def validate_current_label_job_item_number(self, key, current_label_job_item_number):
        assert 0 <= current_label_job_item_number < len(self.label_job_items)
        return current_label_job_item_number


User.label_jobs = relationship("LabelJob", order_by=LabelJob.id, back_populates="user")
