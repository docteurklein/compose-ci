
class CI:
    def __init__(self, fetcher, notifier, get_project, logger, tester, auth=None, mailer=None, garbage_collect=True):
        self.fetcher = fetcher
        self.notifier = notifier
        self.auth = auth
        self.mailer = mailer
        self.get_project = get_project
        self.logger = logger
        self.tester = tester
        self.garbage_collect = garbage_collect

    def run(self, repo, commit, uuid):
        self.logger.info('build uuid: %s' % (uuid))
        self.logger.info('commit: %s#%s' % (repo, commit))
        self.notifier.pending(repo, commit)
        project, result = self.execute(repo, commit, uuid)

        if result.is_success():
            self.notifier.success(repo, commit)
            project.push()
        else:
            self.notifier.failure(repo, commit)

        if self.garbage_collect:
            try:
                project.client.remove_container(uuid, force=True, v=True)
            except:
                pass

        return result

    def execute(self, repo, commit, uuid):
        directory = self.fetcher.fetch(repo, commit)
        project = self.get_project(project_dir=directory, project_name=uuid)
        try:
            self.up(project)
            result = self.tester.test(project, directory)
            self.logger.debug(result)
            self.notify(repo, commit, result)
        finally:
            if self.garbage_collect:
                self.logger.info('putting down %s' % (project.name))
                project.down(include_volumes=True, remove_orphans=True, remove_image_type=False)

        return (project, result)

    def up(self, project):
        self.logger.info('pulling images')
        self.pull(project)
        self.logger.info('building images')
        project.build()
        self.logger.info('reconfiguring services')
        self.reconfigure(project)
        self.logger.info('creating services')
        project.up(do_build=False, detached=True)

    def reconfigure(self, project):
        for service in project.services:
            service.options['ports'] = []

    def pull(self, project):
        self.logger.info('pulling images')
        if self.auth:
            self.auth.login(project)
        project.pull(ignore_pull_failures=True)

    def notify(self, repo, commit, result):
        if not self.mailer:
            return
        subject = '[%s]: %s failed! (exit code: %s)' % (repo, commit[:7], result.code)
        if result.code == 0:
            subject = '[%s]: %s success!' % (repo, commit[:7])
        self.mailer.send(subject, result.to_html())


if __name__ == '__main__':
    import sys
    from .__main__ import ci
    ci().run(sys.argv[1], sys.argv[2], sys.argv[3])
