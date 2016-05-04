
from collections import namedtuple
from ansi2html import Ansi2HTMLConverter

class Result(namedtuple('Result', ['code', 'output'])):
    def to_html(self):
        converter = Ansi2HTMLConverter(
            scheme='solarized',
            dark_bg=True,
            markup_lines=False,
            linkify=True,
        )
        return converter.convert(self.output)

    def is_success(self):
        return self.code == 0
