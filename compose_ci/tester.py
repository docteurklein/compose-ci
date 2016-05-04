
import subprocess, shlex
from .result import Result

class Tester:
    def __init__(self, hook, logger, env={}):
        self.logger = logger
        self.hook = hook
        self.env = env

    def test(self, project, cwd):
        if self.hook:
            args = shlex.split(self.hook)
            self.logger.info('running subprocess %s' % (args))
            process = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                env={**self.env, **{'COMPOSE_PROJECT_NAME': project.name}}
            )

            return Result(code=process.returncode, output=process.stdout.decode())

        # else
        self.logger.info('running default "tests" service')
        service = project.get_service('tests')
        container = service.create_container(one_off=True)
        service.start_container(container)
        container.start()

        return Result(
            code=container.wait(),
            output=container.logs().decode()
        )

