
class Auth:
    def __init__(self, registry, user, password, logger, email=None):
        self.registry = registry
        self.user = user
        self.password = password
        self.email = email
        self.logger = logger

    def login(self, project):
        if not self.user:
            self.logger.info('no user to authenticate')
            return
        self.logger.info('authenticating %s against %s' % (self.user, self.registry))
        project.client.login(self.user, self.password, self.email, self.registry)
