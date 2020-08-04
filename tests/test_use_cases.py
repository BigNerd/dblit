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

    user_codes = (  # user-code
        "daisy.duck",
        "donald.duck"
    )

    label_sets = (  # label-set-code, label-codes
        ("animals",
            ("duck", "goose")
         ),
        ("plants",
            ("flower", "tree")
         )
    )

    item_groups = (  # label-set-code, label-code, uris
        ("animals", "duck", ("urn:1", "urn:2", "urn:3")),
        ("animals", "goose", ("urn:4", "urn:5", "urn:6")),
        ("plants", "flower", ("urn:7", "urn:8", "urn:9")),
        ("plants", "tree", ("urn:10", "urn:11", "urn:12")),
    )

    def setUp(self) -> None:
        connect_string = "sqlite:///:memory:"
        self.app = App(connect_string=connect_string)
        self.session = self.app.create_session()

    def test_use_cases(self):
        for iteration in range(2):  # execute each step twice to check their idempotency
            self.create_label_sets()
            self.create_jobs()
            self.create_users()
            self.assign_jobs()
            self.progress_jobs()
            self.select_job_results()

    def create_label_sets(self):
        for label_set_code, label_codes in self.label_sets:
            label_set = LabelSet.find_or_create(session=self.session, code=label_set_code)
            for label_code in label_codes:
                _ = Label.find_or_create(session=self.session, code=label_code, name=label_code, label_set=label_set)
        self.session.commit()

    def create_jobs(self, max_items_per_job: int = 2):
        for label_set_code, default_label_code, uris in self.item_groups:
            label_set: LabelSet = self.session.query(LabelSet).filter_by(code=label_set_code).first()
            default_label: Label = self.session.query(Label).filter_by(
                code=default_label_code, label_set_id=label_set.id).first()
            job: Optional[Job] = None
            for uri in uris:
                items = Item.find_all_by_label_set_and_uri(session=self.session, label_set=label_set, uri=uri)
                if len(items) == 0:  # here, we only want one item per label set and uri to be worked on
                    if job is None or len(job.items) >= max_items_per_job:
                        job = Job(label_set=label_set, default_label=default_label)
                        self.session.add(job)
                    _ = Item(job=job, uri=uri)
        self.session.commit()

    def create_users(self):
        for user_code in self.user_codes:
            _ = User.find_or_create(session=self.session, code=user_code)
        self.session.commit()

    def assign_jobs(self):
        all_users: List[User] = self.session.query(User).all()
        self.assertEqual(len(self.user_codes), len(all_users))

        unassigned_jobs: List[Job] = self.session.query(Job).filter_by(user_id=None).all()
        for index, job in enumerate(unassigned_jobs):
            job.user = all_users[index % len(all_users)]
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
