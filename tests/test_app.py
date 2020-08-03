from unittest import TestCase

from dblit.app import App


class TestApp(TestCase):

    def setUp(self) -> None:
        connect_string = "sqlite:///:memory:"
        self.app = App(connect_string=connect_string)
        self.session = self.app.create_session()

    def test_app(self):
        self.assertTrue(True)

    def tearDown(self) -> None:
        self.session.commit()
        self.session.close()
