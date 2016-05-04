from .result import Result
from .tester import Tester

class CI:
    def __init__(self, repo, fetcher, notifier, get_project, logger, tester, auth=None, pusher=None, mailer=None, garbage_collect=True):
        self.fetcher = fetcher
        self.notifier = notifier
        self.repo = repo
        self.auth = auth
        self.pusher = pusher
        self.mailer = mailer
        self.get_project = get_project
        self.logger = logger
        self.tester = tester
        self.garbage_collect = garbage_collect

    def run(self, commit, uuid):
        self.logger.info('build uuid: %s' % (uuid))
        self.logger.info('commit: %s' % (commit))
        self.notifier.pending(commit)
        project, result = self.execute(commit, uuid)

        if result.is_success():
            self.notifier.success(commit)
            self.push(project, commit)
        else:
            self.notifier.failure(commit)

        if self.garbage_collect:
            try:
                project.client.remove_container(uuid, force=True, v=True)
            except:
                pass

        return result

    def execute(self, commit, uuid):
        directory = self.fetcher.fetch(commit)
        project = self.get_project(project_dir=directory, project_name=uuid)
        try:
            self.up(project)
            result = self.tester.test(project, directory)
            self.logger.debug(result)
            self.notify(commit, result)
        finally:
            self.logger.info('putting down %s' % (project.name))
            project.down(include_volumes=True, remove_orphans=True, remove_image_type=False)

        return (project, result)

    def up(self, project):
        self.logger.info('pulling images')
        self.pull(project)
        self.logger.info('building images')
        project.build()
        self.logger.info('creating services')
        project.up(do_build=False, detached=True)

    def pull(self, project):
        self.logger.info('pulling images')
        if self.auth:
            self.auth.login(project)
        project.pull()

    def notify(self, commit, result):
        if not self.mailer:
            return
        subject = '[%s]: %s failed! (exit code: %s)' % (self.repo, commit[:7], result.code)
        if result.code == 0:
            subject = '[%s]: %s success!' % (self.repo, commit[:7])
        self.mailer.send(subject, result.to_html())

    def push(self, project, commit):
        if not self.pusher:
            return
        self.pusher.push(commit, project)

if __name__ == '__main__':
    import sys
    from .__main__ import ci
    ci().run(sys.argv[1], sys.argv[2])

