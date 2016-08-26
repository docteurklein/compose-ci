import sys
from os import environ, pathsep
from functools import partial
from .ci import CI
from .cd import CD
from .mailer import Mailer
from .fetcher import Fetcher
from .auth import Auth
from .tester import Tester
from .notifier import Notifier
from .builder import Builder
from .httpd import PostHandler, Httpd
from compose.cli.command import get_project
from docker import Client
import logging

logging.basicConfig(level=environ.get('LOG_LEVEL', logging.INFO), format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

ci = lambda: CI(
    logger    = logger,
    repo      = environ.get('GITHUB_REPO'),
    tester    = Tester(
        hook       = environ.get('HOOK'),
        logger     = logger,
        env        = dict(environ),
    ),
    notifier  = Notifier(
        token      = environ.get('GITHUB_TOKEN'),
        repo      = environ.get('GITHUB_REPO'),
        logger     = logger,
    ),
    fetcher   = Fetcher(
        repo      = environ.get('GITHUB_REPO'),
        token     = environ.get('GITHUB_TOKEN'),
        base_path = environ.get('BASE_PATH', '/tmp/tarball'),
        logger    = logger,
    ),
    auth      = Auth(
        registry = environ.get('DOCKER_REGISTRY'),
        user     = environ.get('REGISTRY_USER'),
        password = environ.get('REGISTRY_PASS'),
        email    = environ.get('REGISTRY_EMAIL'),
        logger   = logger,
    ) if environ.get('REGISTRY_USER') else None,
    mailer    = Mailer(
        From     = environ.get('SMTP_FROM'),
        to       = environ.get('SMTP_TO'),
        host     = environ.get('SMTP_HOST'),
        port     = environ.get('SMTP_PORT'),
        user     = environ.get('SMTP_USER'),
        password = environ.get('SMTP_PASS'),
        logger   = logger,
    ) if environ.get('SMTP_HOST') else None,
    get_project = partial(get_project,
        config_path=environ.get('COMPOSE_FILE', 'docker-compose.yml').split(pathsep)
    ),
    garbage_collect=environ.get('GARBAGE_COLLECT', True)
)

cd = lambda: CD(
    logger    = logger,
    repo      = environ.get('GITHUB_REPO'),
    notifier  = Notifier(
        token      = environ.get('GITHUB_TOKEN'),
        repo      = environ.get('GITHUB_REPO'),
        logger     = logger,
    ),
    fetcher   = Fetcher(
        repo      = environ.get('GITHUB_REPO'),
        token     = environ.get('GITHUB_TOKEN'),
        base_path = environ.get('BASE_PATH', '/tmp/tarball'),
        logger    = logger,
    ),
    auth      = Auth(
        registry = environ.get('DOCKER_REGISTRY'),
        user     = environ.get('REGISTRY_USER'),
        password = environ.get('REGISTRY_PASS'),
        email    = environ.get('REGISTRY_EMAIL'),
        logger   = logger,
    ) if environ.get('REGISTRY_USER') else None,
    get_project = partial(get_project,
        config_path=environ.get('COMPOSE_FILE', 'docker-compose.yml').split(pathsep)
    ),
    garbage_collect=environ.get('GARBAGE_COLLECT', True)
)

httpd = lambda: Httpd(
    addr=(environ.get('BIND', '0.0.0.0'), int(environ.get('PORT', 80))),
    cert=environ.get('CERT_PATH'),
    handler=partial(PostHandler,
        token   = environ.get('GITHUB_TOKEN'),
        builder = Builder(
            image   = environ.get('BUILD_IMAGE'),
            command = environ.get('BUILD_CMD', 'python3 -m compose_ci.ci'),
            binds   = [
                '%s:%s' % (x[7:], x[7:]) for x in [environ.get('DOCKER_HOST')] if x.startswith('unix://')
            ],
            client  = Client(environ.get('DOCKER_HOST')),
            env     = dict(environ)
        )
    )
)

