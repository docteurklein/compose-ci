
from os.path import exists
import shlex

class Builder:
    def __init__(self, image, command, socket, client, env):
        self.image = image
        self.command = command
        self.socket = socket
        self.binds = [
            '%s:%s' % (x[7:], x[7:]) for x in [self.socket] if x.startswith('unix://')
        ]
        self.client = client
        self.env = env

    def build(self, commit, id):
        container = self.client.create_container(
            host_config=self.client.create_host_config(binds=self.binds),
            name=id,
            tty=True,
            environment=self.env,
            image=self.image,
            command=shlex.split(self.command) + [commit, id]
        )
        self.client.start(container.get('Id'))

