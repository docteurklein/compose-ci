
class CD:
    def __init__(self, repo, fetcher, notifier, get_project, logger, auth=None, garbage_collect=True):
        self.fetcher = fetcher
        self.notifier = notifier
        self.repo = repo
        self.auth = auth
        self.get_project = get_project
        self.logger = logger
        self.garbage_collect = garbage_collect

    def run(self, commit, uuid):
        self.logger.info('build uuid: %s' % (uuid))
        self.logger.info('commit: %s' % (commit))
        self.notifier.pending(commit)
        directory = self.fetcher.fetch(commit)
        project = self.get_project(project_dir=directory, project_name=uuid)
        self.up(project, commit)
        self.notifier.success(commit)

        if self.garbage_collect:
            try:
                project.client.remove_container(uuid, force=True, v=True)
            except:
                pass

    def up(self, project, commit):
        self.logger.info('pulling images')
        #self.pull(project)
        self.logger.info('building images')
        #project.build()
        self.logger.info('reconfiguring services')
        self.reconfigure(project, commit)
        self.logger.info('creating services')
        project.up(do_build=False, detached=True)

    def reconfigure(self, project, commit):
        for service in project.services:
            service.options['ports'] = []
            service.options['publish_all'] = True

            #service.options['environment'] = service.options.get('environment', {})
            #service.options['environment']['VIRTUAL_HOST'] = '%s.%s.127.0.0.1.xip.io' % (service.name, commit[:7])

    def pull(self, project):
        self.logger.info('pulling images')
        if self.auth:
            self.auth.login(project)
        project.pull(ignore_pull_failures=True)

if __name__ == '__main__':
    import sys
    from .__main__ import cd
    cd().run(sys.argv[1], sys.argv[2])
