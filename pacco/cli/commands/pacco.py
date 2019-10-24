from pacco.cli.commands.utils.command_abstract import CommandAbstract
from pacco.cli.commands import remote, registry, binary
from pacco.cli.commands.utils.output_stream import OutputStream
from pacco.manager.remote_manager import RemoteManager


class Pacco(CommandAbstract):
    def remote(self, *args: str):
        remote.Remote('remote', self.out, self.rm).run(*args)

    def registry(self, *args: str):
        registry.Registry('registry', self.out, self.rm).run(*args)

    def binary(self, *args: str):
        binary.Binary('binary', self.out, self.rm).run(*args)


def main(args):
    Pacco('', OutputStream(), RemoteManager()).run(*args)
