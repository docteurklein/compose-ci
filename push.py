#!/usr/bin/env python

from compose.cli.command import project_from_options
from docker.auth import auth
from docker.utils import utils
from os import environ
import sys

project = project_from_options('.', {})

for service in project.get_services():
    if service.image_name.startswith(environ.get('DOCKER_REGISTRY')):
        tag = sys.argv[1]
        repository, actual_tag = utils.parse_repository_tag(service.image_name)
        registry, image = auth.resolve_repository_name(repository)
        project.client.tag(image, repository, tag)
        project.client.push(repository, tag)
        print(image, repository, tag)

