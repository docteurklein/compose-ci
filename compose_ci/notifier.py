
from urllib import request

class Notifier:
    def __init__(self, repo, token, logger):
        self.repo = repo
        self.token = token
        self.logger = logger

    def pending(self, commit, target=''):
        self.post(commit, 'pending', target)

    def success(self, commit, target=''):
        self.post(commit, 'success', target)

    def failure(self, commit, target=''):
        self.post(commit, 'failure', target)

    def post(self, commit, state, target=''):
        url = 'https://api.github.com/repos/%s/statuses/%s' % (self.repo, commit)
        data = '{"state": "%s", "context": "[%s CI]", "target_url": "%s"}' % (state, self.repo, target)
        self.logger.info('notifying %s for %s' % (data, url))
        req = request.Request(url=url, data=data)
        if self.token:
            req.add_header('Authorization', 'token %s' % (self.token))
        with request.urlopen(req, data=data.encode()) as res:
            self.logger.info(res.status)

