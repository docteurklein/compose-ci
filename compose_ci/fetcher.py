from urllib import request
from os import path
import tarfile

class Fetcher:
    def __init__(self, repo, base_path, token, logger):
        self.repo = repo
        self.base_path = base_path
        self.token = token
        self.logger = logger

    def fetch(self, commit):
        url = 'https://api.github.com/repos/%s/tarball/%s' % (self.repo, commit)
        self.logger.info('fetching %s' % (url))
        req = request.Request(url)
        if self.token:
            req.add_header('Authorization', 'token %s' % (self.token))

        with request.urlopen(req) as res:
            with tarfile.open(fileobj=res, mode='r:gz') as archive:
                directory = archive.next()
                self.logger.info('extracting %s' % (directory.name))
                archive.extractall(self.base_path)
                return path.join(self.base_path, directory.name)

