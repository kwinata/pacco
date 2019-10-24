import inspect
from typing import Dict, Callable

from pacco import __version__ as client_version


class CommandAbstract:
    def __init__(self, name, output, remote_manager):
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
        namespace = self.__name
        stream = self.__out
        max_len = max((len("pacco {} {}".format(namespace, c)) for c in commands)) + 1
        fmt = '  %-{}s'.format(max_len)
        for name in commands:
            appended_name = "pacco {} {}".format(namespace, name)
            print(fmt % appended_name, end="")
            stream.writeln(CommandAbstract.__format_docstring(commands[name].__doc__))
        stream.writeln("")
        stream.writeln("Pacco {} commands. Type 'pacco {} <command> -h' for help".format(namespace, namespace))

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
