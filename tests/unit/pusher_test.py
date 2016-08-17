from unittest import mock, TestCase

from compose.project import Project
from compose.service import Service
import docker

from compose_ci.pusher import Pusher

class TestPusher(TestCase):

    def test_it_pushes_commit_tag(self):

        project = mock.create_autospec(Project)
        project.client = mock.create_autospec(docker.Client)
        project.get_services.return_value = [mock.create_autospec(Service)]

        pusher = Pusher(
            registry='test.com/test',
        )
        pusher.push('123', project)

        project.client.push.assert_called_with(mock.ANY, '123', stream=True)

    def test_it_pushes_with_default_tag(self):

        project = mock.create_autospec(Project)
        project.client = mock.create_autospec(docker.Client)
        project.get_services.return_value = [mock.create_autospec(Service)]

        pusher = Pusher(
            registry='test.com/test',
            tag='FORCED_TAG'
        )
        pusher.push('123', project)

        project.client.push.assert_called_with(mock.ANY, 'FORCED_TAG', stream=True)
