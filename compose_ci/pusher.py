
from docker.utils import utils
import concurrent.futures
import sys

class Pusher:
    def __init__(self, registry, tag=None):
        self.registry = registry
        self.tag = tag

    def push(self, tag, project):
        tag = self.tag or tag
        with concurrent.futures.ThreadPoolExecutor() as e:
            for image in self.extract(project):
                project.client.tag(image, image, tag)
                e.submit(self.display, image, project.client.push(image, tag, stream=True))

    def extract(self, project):
        for service in project.get_services():
            if not service.image_name.startswith(self.registry):
                continue
            repository, actual_tag = utils.parse_repository_tag(service.image_name)
            yield repository

    def display(self, image, output):
        for line in output:
            sys.stdout.write('\033[2J')
            sys.stdout.write('\033[H')
            sys.stdout.write('%s: %s\r' % (image, line))
            sys.stdout.flush()
