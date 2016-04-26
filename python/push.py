#!/usr/bin/env python

from compose.cli.command import project_from_options
from docker.auth import auth
from docker.utils import utils
from os import environ
import concurrent.futures
import sys

project = project_from_options('.', {})

def display(repository, output):
    for line in output:
        sys.stdout.write('\033[2J')
        sys.stdout.write('\033[H')
        sys.stdout.write('%s: %s\r' % (repository, line))
        sys.stdout.flush()

with concurrent.futures.ThreadPoolExecutor() as e:
    for service in project.get_services():
        if service.image_name.startswith(environ.get('DOCKER_REGISTRY')):
            tag = sys.argv[1]
            repository, actual_tag = utils.parse_repository_tag(service.image_name)
            project.client.tag(repository, repository, tag)
            e.submit(display, repository, project.client.push(repository, tag, stream=True))

