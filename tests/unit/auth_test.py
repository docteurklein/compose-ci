from unittest import mock, TestCase

from compose.project import Project
from compose.service import Service
import docker

from compose_ci.auth import Auth
import logging

class TestAuth(TestCase):

    def test_it_logins_against_the_registry(self):

        project = mock.create_autospec(Project)
        project.client = mock.create_autospec(docker.Client)
        logger = mock.create_autospec(logging.Logger)

        auth = Auth(
            user='test',
            password='test',
            email='test',
            registry='example.org',
            logger=logger
        )
        auth.login(project)

        project.client.login.assert_called_with('test', 'test', 'test', 'example.org')

