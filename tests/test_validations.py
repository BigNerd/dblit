from unittest import TestCase

from sqlalchemy.exc import IntegrityError

from dblit.app import App
from dblit.user import User
from dblit.job import Job
from dblit.label_set import LabelSet
from dblit.label import Label


class TestValidations(TestCase):

    def setUp(self) -> None:
        connect_string = "sqlite:///:memory:"
        self.app = App(connect_string=connect_string)
        self.session = self.app.create_session()

    def test_create_user_without_code(self):
        with self.assertRaises(AssertionError):  # because user has no code
            _ = User(code=None)

    def test_create_users_with_same_codes(self):
        user_1 = User(code="same")
        user_2 = User(code="same")
        self.session.add(user_1)
        self.session.add(user_2)
        with self.assertRaises(IntegrityError):  # because two users have the same code
            self.session.commit()
        self.session.rollback()

    def test_create_job_with_inconsistent_label_set_and_default_label(self):
        label_set_1 = LabelSet(code="label_set_1")
        label_set_2 = LabelSet(code="label_set_2")

        label_2 = Label(code="label_2", name="label_2", label_set=label_set_2)

        with self.assertRaises(AssertionError):  # because label_2 is not in label_set_1
            _ = Job(label_set=label_set_1, default_label=label_2)
        self.session.rollback()

    def tearDown(self) -> None:
        self.session.commit()
        self.session.close()
