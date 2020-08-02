from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dblit.base import Base
from dblit.user import User
from dblit.label_job import LabelJob


class App:

    def __init__(self, connect_string: str):
        self.__engine = create_engine(connect_string, echo=True)
        Base.metadata.create_all(self.__engine)

    def create_session(self):
        session = sessionmaker(bind=self.__engine)()
        return session

#user_name = ""
#password = ""
#host = ""
#db_name = ""
#connect_string: str = f"mysql+pymysql://{user_name}>:{password}>@{host}/{db_name}"
