from pacco.cli.commands.binary import Binary
from pacco.cli.commands.registry import Registry
from pacco.cli.commands.remote import Remote
from pacco.cli.commands.utils.command_abstract import CommandAbstract


class Pacco(CommandAbstract):
    def remote(self, *args: str):
        Remote('remote', self.out).run(*args)

    def registry(self, *args: str):
        Registry('registry', self.out).run(*args)

    def binary(self, *args: str):
        Binary('binary', self.out).run(*args)
