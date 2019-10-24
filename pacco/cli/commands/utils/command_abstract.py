import argparse
import inspect
from typing import Dict, Callable

from pacco import __version__ as client_version


class CommandAbstract:
    def __init__(self, name, output, remote_manager):
        if name:
            name += " "  # see show help below, we don't want double space for empty `name`
        self.__name = name
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
            elif command in ["-v", "--version"]:
                self.__out.writeln("Pacco version {}".format(client_version))
                return
            self.__out.writeln(
                "'pacco {NAME} {COMMAND}' is an invalid command. See 'pacco {NAME} --help'.".format(
                    NAME=self.__name,
                    COMMAND=command),
                error=True
            )
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
        max_len = max(
            (
                len("pacco {NAME}{COMMAND}".format(NAME=self.__name, COMMAND=command))
                for command in commands
            )) + 1
        fmt = '  %-{}s'.format(max_len)
        for command in commands:
            appended_name = "pacco {NAME}{COMMAND}".format(NAME=self.__name, COMMAND=command)
            print(fmt % appended_name, end="")
            self.__out.writeln(CommandAbstract.__format_docstring(commands[command].__doc__))
        self.__out.writeln("")
        self.__out.writeln("Pacco {NAME}commands. Type 'pacco {NAME}<command> -h' for help".format(NAME=self.__name))

    @staticmethod
    def __format_docstring(docstring: str) -> str:
        if not docstring:
            return ''
        docstring_lines = docstring.split('\n')
        data = []
        for line in docstring_lines:
            line = line.strip()
            data.append(line)
        return ' '.join(data)

    def init_parser(self, method_name: str):
        return argparse.ArgumentParser(prog="pacco {NAME}{COMMAND}".format(NAME=self.__name, COMMAND=method_name))
