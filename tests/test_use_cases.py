from random import randint
from typing import List, Optional, Tuple
from unittest import TestCase

from dblit.app import App
from dblit.item import Item
from dblit.job import Job
from dblit.label import Label
from dblit.label_set import LabelSet
from dblit.user import User


class TestUseCases(TestCase):

    user_codes = (
        "daisy.duck",
        "donald.duck"
    )

    label_sets = (
        ("animals",
            ("duck", "goose")
         ),
        ("plants",
            ("flower", "tree")
         )
    )

    item_groups = (
        ("animals", "duck", ("urn:1", "urn:2", "urn:3")),
        ("animals", "goose", ("urn:4", "urn:5", "urn:6")),
        ("plants", "flower", ("urn:7", "urn:8", "urn:9")),
        ("plants", "tree", ("urn:10", "urn:11", "urn:12")),
    )

    def setUp(self) -> None:
        connect_string = "sqlite:///:memory:?cache=shared"
        self.app = App(connect_string=connect_string)
        self.session = self.app.create_session()

    def test_use_cases(self):
        self.create_label_sets()
        self.create_jobs()
        self.create_users()
        self.assign_jobs()
        self.progress_jobs()
        self.select_job_results()

    def create_label_sets(self):
        for label_set_code, label_codes in self.label_sets:
            label_set = LabelSet(code=label_set_code)
            for label_code in label_codes:
                _ = Label(code=label_code, name=label_code, label_set=label_set)
            self.session.add(label_set)
        self.session.commit()

    def create_jobs(self):
        for label_set_code, default_label_code, uris in self.item_groups:
            label_set: LabelSet = self.session.query(LabelSet).filter_by(code=label_set_code).first()
            default_label: Label = self.session.query(Label).filter_by(
                code=default_label_code, label_set_id=label_set.id).first()
            job = Job(label_set=label_set, default_label=default_label)
            self.session.add(job)
            for uri in uris:
                _ = Item(job=job, uri=uri)
        self.session.commit()

    def create_users(self):
        for user_code in self.user_codes:
            user = User(code=user_code)
            self.session.add(user)
        self.session.commit()

    def assign_jobs(self):
        selected_users: List[User] = self.session.query(User).all()
        self.assertEqual(len(self.user_codes), len(selected_users))

        selected_jobs: List[Job] = self.session.query(Job).all()
        self.assertTrue(len(self.item_groups) <= len(selected_jobs))

        for index, job in enumerate(selected_jobs):
            job.user = selected_users[index % len(selected_users)]
        self.session.commit()

    def progress_jobs(self):
        for user_code in self.user_codes:
            user: User = self.session.query(User).filter_by(code=user_code).first()
            jobs: List[Job] = self.session.query(Job).filter_by(user_id=user.id).all()
            for job in jobs:
                label_set: LabelSet = self.session.query(LabelSet).filter_by(id=job.label_set_id).first()
                default_label: Label = self.session.query(Label).filter_by(id=job.default_label_id).first()
                items: List[Item] = job.items
                items.sort(key=lambda _item: _item.id)  # ascending order required for correct current_item_index update
                for item in items:
                    random_override_label_index: int = randint(0, len(label_set.labels) - 1)
                    item.override_label = label_set.labels[random_override_label_index]
                    if item.override_label.id == default_label.id:
                        item.override_label = None  # no need to set the default as override, so undo
                    job.current_item_index = items.index(item)
        self.session.commit()

    def select_job_results(self):
        job_results: List[Tuple[str, str]] = []
        for label_set_code, default_label_code, uris in self.item_groups:
            label_set: LabelSet = self.session.query(LabelSet).filter_by(code=label_set_code).first()
            default_label: Label = self.session.query(Label).filter_by(
                label_set_id=label_set.id, code=default_label_code).first()
            jobs: List[Job] = self.session.query(Job).filter_by(
                label_set_id=label_set.id, default_label_id=default_label.id)
            for job in jobs:
                items: List[Item] = self.session.query(Item).filter_by(job_id=job.id)
                for item in items:
                    uri = item.uri
                    label: Optional[Label] = item.override_label
                    if label is None:
                        label = default_label
                    label_code = label.code
                    job_results.append((uri, label_code))
        expected_number_of_items: int = sum([len(item_group[2]) for item_group in self.item_groups])
        self.assertEqual(expected_number_of_items, len(job_results))
        self.session.commit()

    def tearDown(self) -> None:
        self.session.commit()
        self.session.close()
