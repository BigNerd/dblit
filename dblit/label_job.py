from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dblit.base import Base
from dblit.user import User


class LabelJob(Base):
    __tablename__ = 'label_job'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", backref="label_job")

    def __init__(self, user):
        self.user = user


User.label_jobs = relationship("LabelJob", order_by=LabelJob.id, back_populates="user")
