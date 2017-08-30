from unittest import mock, TestCase

from compose_ci.ci import CI
from compose_ci.fetcher import Fetcher
from compose_ci.auth import Auth
from compose_ci.mailer import Mailer
from compose_ci.tester import Tester
from compose_ci.result import Result
from compose_ci.notifier import Notifier
from compose.project import Project
from compose.service import Service
import logging

class TestCI(TestCase):

    def setUp(self):
        self.fetcher = mock.create_autospec(Fetcher)
        self.fetcher.fetch.return_value = '/some/path'
        self.auth = mock.create_autospec(Auth)
        self.mailer = mock.create_autospec(Mailer)
        self.project = mock.create_autospec(Project)
        self.notifier = mock.create_autospec(Notifier)
        self.project.name = '123'
        self.service = mock.create_autospec(Service)
        self.service.options = {'ports': ['80:80']}
        self.project.services = [self.service]
        self.get_project = mock.Mock()
        self.get_project.return_value = self.project
        self.logger = mock.create_autospec(logging.Logger)
        self.tester = mock.create_autospec(Tester)

        self.ci = CI(
            fetcher=self.fetcher,
            auth=self.auth,
            mailer=self.mailer,
            get_project=self.get_project,
            logger=self.logger,
            tester=self.tester,
            notifier=self.notifier,
        )

    def test_it_integrates_continuously(self):

        self.tester.test.return_value = Result(0, 'yay')

        self.ci.run('some/repo', '345234c7f914a2431c116cc8840736710105b78e', '123')

        self.get_project.assert_called_with(project_dir='/some/path', project_name='123')
        self.auth.login.assert_called_with(self.project)
        self.mailer.send.assert_called_with(mock.ANY, mock.ANY)
        self.project.push.assert_called_with()
        self.project.down.assert_called_with(include_volumes=True, remove_orphans=True, remove_image_type=False)

    def test_it_pushes_only_on_succsss(self):

        self.tester.test.return_value = Result(1, 'nope')

        self.ci.run('some/repo', '345234c7f914a2431c116cc8840736710105b78e', '123')

        self.get_project.assert_called_with(project_dir='/some/path', project_name='123')
        self.auth.login.assert_called_with(self.project)
        self.mailer.send.assert_called_with(mock.ANY, mock.ANY)
        self.project.push.assert_not_called()

    def test_it_reconfigures_ports(self):

        self.ci.run('some/repo', '345234c7f914a2431c116cc8840736710105b78e', '123')
        self.assertEqual(self.service.options.get('ports'), [])
