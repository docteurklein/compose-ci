
from urllib import request

class Notifier:
    def __init__(self, token, logger):
        self.token = token
        self.logger = logger

    def pending(self, repo, commit, target=''):
        self.post(repo, commit, 'pending', target)

    def success(self, repo, commit, target=''):
        self.post(repo, commit, 'success', target)

    def failure(self, repo, commit, target=''):
        self.post(repo, commit, 'failure', target)

    def post(self, repo, commit, state, target=''):
        url = 'https://api.github.com/repos/%s/statuses/%s' % (repo, commit)
        data = '{"state": "%s", "context": "[%s CI]", "target_url": "%s"}' % (state, repo, target)
        self.logger.info('notifying %s for %s' % (data, url))
        req = request.Request(url=url, data=data)
        if self.token:
            req.add_header('Authorization', 'token %s' % (self.token))
        with request.urlopen(req, data=data.encode()) as res:
            self.logger.info(res.status)

