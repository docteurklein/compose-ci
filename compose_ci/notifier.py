
from urllib import request

class Notifier:
    def __init__(self, repo, token, logger):
        self.repo = repo
        self.token = token
        self.logger = logger

    def pending(self, commit):
        self.post(commit, 'pending')

    def success(self, commit):
        self.post(commit, 'success')

    def failure(self, commit):
        self.post(commit, 'failure')

    def post(self, commit, state):
        url = 'https://api.github.com/repos/%s/statuses/%s' % (self.repo, commit)
        data = '{"state": "%s", "context": "[%s ci]"}' % (state, self.repo)
        self.logger.info('notifying %s for %s' % (data, url))
        req = request.Request(url=url, data=data)
        if self.token:
            req.add_header('Authorization', 'token %s' % (self.token))
        with request.urlopen(req, data=data.encode()) as res:
            self.logger.info(res.status)

