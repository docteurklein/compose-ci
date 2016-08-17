from unittest import mock, TestCase

from compose_ci.tester import Tester
from compose_ci.result import Result
from compose.project import Project
from compose.service import Service
import logging

class TestTester(TestCase):

    def setUp(self):
        self.project = mock.create_autospec(Project)
        self.project.name = '123'
        self.logger = mock.create_autospec(logging.Logger)

    def test_it_executes_custom_hook(self):

        self.tester = Tester(
            hook='echo "yay!"',
            logger=self.logger,
        )

        result = self.tester.test(self.project, None)

        self.assertEqual(result.output, 'yay!\n')

    def test_it_runs_the_convention_based_tests_service(self):

        self.project.get_service.return_value = mock.create_autospec(Service)
        self.project.get_service('tests').create_container().logs.return_value = b'oh you'

        self.tester = Tester(
            hook=None,
            logger=self.logger,
        )

        result = self.tester.test(self.project, '/some/path')

        self.assertEqual(result.output, 'oh you')
