import inspect
from typing import Dict, Callable

from pacco.manager.remote_manager import RemoteManager


class CommandAbstract:
    def __init__(self, output, remote_manager: RemoteManager):
        self.__out = output
        self.__rm = remote_manager

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
            self.__out.writeln(
                "'pacco binary {}' is an invalid command. See 'pacco binary --help'.".format(command),
                error=True)
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
        utils.show_help(self.__get_commands(), 'binary', self.__out)
