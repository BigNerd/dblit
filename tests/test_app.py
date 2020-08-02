from unittest import TestCase

from dblit.app import App
from dblit.user import User
from dblit.label_job import LabelJob


class TestApp(TestCase):

    def setUp(self) -> None:
        connect_string = "sqlite:///:memory:"
        self.app = App(connect_string=connect_string)
        self.session = self.app.create_session()

    def test_create_user(self):
        user_name = "daisy.duck"
        user = self.create_user(user_name=user_name)
        selected_user: User = self.session.query(User).filter_by(name=user_name).first()
        self.assertEqual(user.name, selected_user.name)

    def test_create_label_job(self):
        user = self.create_user()
        label_job = LabelJob(user=user)
        self.session.add(label_job)
        self.session.flush()
        self.assertIn(label_job, user.label_jobs)

    def create_user(self, user_name: str = "donald.duck") -> User:
        user = User(name=user_name)
        self.session.add(user)
        return user

    def tearDown(self) -> None:
        self.session.commit()
        self.session.close()
