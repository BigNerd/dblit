from unittest import TestCase

from dblit.app import App
from dblit.user import User
from dblit.label_job import LabelJob
from dblit.label_job_item import LabelJobItem
from dblit.label_set import LabelSet
from dblit.label_set_item import LabelSetItem
from dblit.label import Label


class TestApp(TestCase):

    def setUp(self) -> None:
        connect_string = "sqlite:///:memory:"
        self.app = App(connect_string=connect_string)
        self.session = self.app.create_session()

    def test_create_user(self):
        user_code = "daisy.duck"
        user = self.create_user(user_code=user_code)
        selected_user: User = self.session.query(User).filter_by(name=user_code).first()
        self.assertEqual(user.name, selected_user.name)

    def test_create_label_set(self):
        label_set = self.create_label_set()
        label_duck = Label(code="duck", name="duck", label_set=label_set)
        label_goose = Label(code="goose", name="goose", label_set=label_set)

        self.assertIn(label_duck, label_set.labels)
        self.assertEqual(label_duck.label_set, label_set)

        self.assertIn(label_goose, label_set.labels)
        self.assertEqual(label_goose.label_set, label_set)

    def test_create_label_set_item(self):
        label_set = self.create_label_set()
        label = Label(code="my_label", name="my_label", label_set=label_set)
        uri = "http://my.resource.org"
        label_set_item = LabelSetItem(uri=uri, label=label)
        self.assertEqual(label_set_item.uri, uri)
        self.assertEqual(label_set_item.label, label)
        self.session.add(label_set_item)

    def test_create_label_job(self):
        user = self.create_user()

        label_set = self.create_label_set()
        label_1 = Label(code="label_1", name="label_1", label_set=label_set)
        label_2 = Label(code="label_2", name="label_2", label_set=label_set)

        label_set_item_1 = LabelSetItem(uri="uri_1", label=label_1)
        label_set_item_2 = LabelSetItem(uri="uri_2", label=label_2)

        label_job = LabelJob(user=user, label_set=label_set)

        label_job_item_1 = LabelJobItem(label_job=label_job, label_set_item=label_set_item_1)
        label_job_item_2 = LabelJobItem(label_job=label_job, label_set_item=label_set_item_2)

        label_job.current_label_job_item_number = 0

        self.assertIn(label_job, user.label_jobs)
        self.assertEqual(user, label_job.user)

        self.assertIn(label_job_item_1, label_job.label_job_items)
        self.assertEqual(label_job, label_job_item_1.label_job)

        self.assertIn(label_job_item_2, label_job.label_job_items)
        self.assertEqual(label_job, label_job_item_2.label_job)

    def test_create_label_job_with_inconsistent_label_sets(self):
        label_set_1 = self.create_label_set(label_set_code="1")
        label_set_2 = self.create_label_set(label_set_code="2")

        label = Label(code="label", name="label", label_set=label_set_2)
        label_set_item = LabelSetItem(uri="uri_1", label=label)

        # use a label set which is not the same as the one associated with the label set item
        label_job = LabelJob(user=self.create_user(), label_set=label_set_1)

        with self.assertRaises(AssertionError):
            _ = LabelJobItem(label_job=label_job, label_set_item=label_set_item)

    def create_user(self, user_code: str = "donald.duck") -> User:
        user = User(code=user_code, name=user_code)
        self.session.add(user)
        return user

    def create_label_set(self, label_set_code: str = "animals") -> LabelSet:
        label_set = LabelSet(code=label_set_code, name=label_set_code)
        self.session.add(label_set)
        return label_set

    def tearDown(self) -> None:
        self.session.commit()
        self.session.close()
