#!/usr/bin/env python

from compose.cli.command import project_from_options
from docker.auth import auth
from docker.utils import utils
from os import environ
import concurrent.futures
import sys

project = project_from_options('.', {})

def display(project, repository, tag):
    for x in project.client.push(repository, tag, stream=True):
        #sys.stdout.write(chr(27) + '[2K')
        print("%s: %s" % (repository, x))

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:
    for service in project.get_services():
        if service.image_name.startswith(environ.get('DOCKER_REGISTRY')):
            tag = sys.argv[1]
            repository, actual_tag = utils.parse_repository_tag(service.image_name)
            registry, image = auth.resolve_repository_name(repository)
            project.client.tag(repository, repository, tag)
            e.submit(display, project, repository, tag)

