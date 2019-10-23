import inspect
from typing import Callable, Dict

from pacco import __version__ as client_version
from pacco.cli import remote, registry, binary
from pacco.cli.output_stream import OutputStream
from pacco.manager.remote_manager import RemoteManager


class CommandManager:
    def __init__(self):
        self.__out = OutputStream()
        self.__rm = RemoteManager()

    def run(self, *args):
        """
        Entry point for executing commands, dispatcher to class methods.
        """
        if not args:
            self.__show_help()
            return
        command = args[0]
        remaining_args = args[1:]
        commands = self.__get_commands()
        if command not in commands:
            if command in ["-h", "--help"]:
                self.__show_help()
                return
            elif command in ["-v", "--version"]:
                self.__out.writeln("Pacco version {}".format(client_version))
                return
            self.__out.writeln("'pacco {}' is an invalid command. See 'pacco --help'.".format(command), error=True)
            return
        method = commands[command]
        method(*remaining_args)

    def __get_commands(self) -> Dict[str, Callable]:
        result = {}
        for method_name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if not method_name.startswith('_') and method_name not in ["run"]:
                result[method_name] = method
        return result

    def __show_help(self):
        commands = self.__get_commands()
        max_len = max((len("pacco {}".format(c)) for c in commands)) + 1
        fmt = '  %-{}s'.format(max_len)
        for name in commands:
            appended_name = "pacco {}".format(name)
            print(fmt % appended_name, end="")
            if commands[name].__doc__:
                docstring_lines = commands[name].__doc__.split('\n')
                data = []
                for line in docstring_lines:
                    line = line.strip()
                    data.append(line)
                self.__out.writeln(' '.join(data))
            else:
                self.__out.writeln("")  # Empty docs
        self.__out.writeln("")
        self.__out.writeln("Pacco commands. Type 'pacco <command> -h' for help")

    def remote(self, *args: str):
        remote.Remote(self.__out, self.__rm).run(*args)

    def registry(self, *args: str):
        registry.Registry(self.__out, self.__rm).run(*args)

    def binary(self, *args: str):
        binary.Binary(self.__out, self.__rm).run(*args)


def main(args):
    CommandManager().run(*args)
