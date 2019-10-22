import argparse
import inspect
import re
from typing import Callable, Dict

from pacco import __version__ as client_version
from pacco.cli.output_stream import OutputStream
from pacco.remote_manager import RemoteManager, ALLOWED_REMOTE_TYPES


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
        Remote(self.__out, self.__rm).run(*args)

    def registry(self, *args: str):
        Registry(self.__out, self.__rm).run(*args)

    def binary(self, *args: str):
        Binary(self.__out, self.__rm).run(*args)


class Remote:
    def __init__(self, output: OutputStream, remote_manager: RemoteManager):
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
            self.__out.writeln("'pacco remote {}' is an invalid command. See 'pacco remote --help'.".format(command),
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
        commands = self.__get_commands()
        max_len = max((len("pacco remote {}".format(c)) for c in commands)) + 1
        fmt = '  %-{}s'.format(max_len)
        for name in commands:
            appended_name = "pacco remote {}".format(name)
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
        self.__out.writeln("Pacco remote commands. Type 'pacco remote <command> -h' for help")

    def list(self, *args):
        """
        List existing remotes.
        """
        parser = argparse.ArgumentParser(prog="pacco remote list")
        parser.parse_args(args)
        remotes = self.__rm.list_remote()
        self.__out.writeln(remotes)

    def add(self, *args):
        """
        Add a remote.
        """
        parser = argparse.ArgumentParser(prog="pacco remote add")
        parser.add_argument("name", help="remote name")
        parser.add_argument("type", help="remote type", choices=ALLOWED_REMOTE_TYPES)
        parsed_args = parser.parse_args(args)
        if parsed_args.type == "local":
            path = input("Path (if empty, ~/.pacco/ will be used): ")
            self.__rm.add_remote(parsed_args.name, {
                "remote_type": "local",
                "path": path
            })
        elif parsed_args.type == "nexus_site":
            url = input("URL: ")
            username = input("Username: ")
            from getpass import getpass
            password = getpass()
            self.__rm.add_remote(parsed_args.name, {
                "remote_type": "nexus_site",
                "url": url,
                "username": username,
                "password": password
            })

    def remove(self, *args):
        """
        Remove a remote.
        """
        parser = argparse.ArgumentParser(prog="pacco remote remove")
        parser.add_argument("name", help="remote name")
        parsed_args = parser.parse_args(args)
        self.__rm.remove_remote(parsed_args.name)

    def set_default(self, *args):
        """
        Set default remote(s).
        """
        parser = argparse.ArgumentParser(prog="pacco remote set_default")
        parser.add_argument("name", nargs="*", help="remote name")
        parsed_args = parser.parse_args(args)
        self.__rm.set_default(parsed_args.name)

    def list_default(self, *args):
        """
        List default remote(s).
        """
        parser = argparse.ArgumentParser(prog="pacco remote list_default")
        parser.parse_args(args)
        default_remotes = self.__rm.get_default()
        self.__out.writeln(default_remotes)


class Registry:
    def __init__(self, output: OutputStream, remote_manager: RemoteManager):
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
                "'pacco registry {}' is an invalid command. See 'pacco registry --help'.".format(command),
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
        commands = self.__get_commands()
        max_len = max((len("pacco registry {}".format(c)) for c in commands)) + 1
        fmt = '  %-{}s'.format(max_len)
        for name in commands:
            appended_name = "pacco registry {}".format(name)
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
        self.__out.writeln("Pacco registry commands. Type 'pacco registry <command> -h' for help")

    def list(self, *args):
        """
        List registries of a remote.
        """
        parser = argparse.ArgumentParser(prog="pacco registry list")
        parser.add_argument("remote", help="remote name")
        parsed_args = parser.parse_args(args)
        pm = self.__rm.get_remote(parsed_args.remote)
        self.__out.writeln(pm.list_package_registries())

    def add(self, *args):
        """
        Add registry to remote.
        """
        parser = argparse.ArgumentParser(prog="pacco registry add")
        parser.add_argument("remote", help="remote name")
        parser.add_argument("name", help="registry name")
        parser.add_argument("settings", help="settings key (e.g. os,version,obfuscation)")
        parsed_args = parser.parse_args(args)
        if not re.match(r"([(\w)-.]+,)*([(\w)-.]+),?", parsed_args.settings):
            raise ValueError("Settings must be in the form of ([(\\w)-.]+,)*([(\\w)-.]+),?")
        pm = self.__rm.get_remote(parsed_args.remote)
        pm.add_package_registry(parsed_args.name, parsed_args.settings.split(","))

    def remove(self, *args):
        """
        Remove a registry from a specific remote.
        """
        parser = argparse.ArgumentParser(prog="pacco registry remove")
        parser.add_argument("remote", help="remote name")
        parser.add_argument("name", help="registry name")
        parsed_args = parser.parse_args(args)
        pm = self.__rm.get_remote(parsed_args.remote)
        pm.remove_package_registry(parsed_args.name)

    def binaries(self, *args):
        """
        List binaries of a registry from a specific remote.
        """
        parser = argparse.ArgumentParser(prog="pacco registry binaries")
        parser.add_argument("remote", help="remote name")
        parser.add_argument("name", help="registry name")
        parsed_args = parser.parse_args(args)
        pm = self.__rm.get_remote(parsed_args.remote)
        pr = pm.get_package_registry(parsed_args.name)
        self.__out.writeln(pr.list_package_binaries())


class Binary:
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
        commands = self.__get_commands()
        max_len = max((len("pacco binary {}".format(c)) for c in commands)) + 1
        fmt = '  %-{}s'.format(max_len)
        for name in commands:
            appended_name = "pacco binary {}".format(name)
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
        self.__out.writeln("Pacco binary commands. Type 'pacco binary <command> -h' for help")

    @staticmethod
    def __parse_settings_args(settings_args: str) -> Dict[str, str]:
        if not re.match(r"([\w\-.]+=[\w\-.]+,)*([\w\-.]+=[\w\-.]+),?", settings_args):
            raise ValueError("The settings configuration must match ([\\w-.]+=[\\w-.]+,)*([\\w-.]+=[\\w-.]+),?")
        return {token.split('=')[0]: token.split('=')[1] for token in settings_args.split(',')}

    def download(self, *args):
        parser = argparse.ArgumentParser(prog="pacco binary download")
        parser.add_argument("remote_name", help="remote name")
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("dir_path", help="download path")
        parser.add_argument("settings", help="settings for the specified registry "
                                             "(e.g. os=linux,version=2.1.0,type=debug")
        parsed_args = parser.parse_args(args)

        settings_dict = Binary.__parse_settings_args(parsed_args.settings)
        if parsed_args.remote_name == 'default':
            self.__rm.default_download(parsed_args.registry_name, settings_dict, parsed_args.dir_path)
        pm = self.__rm.get_remote(parsed_args.remote_name)
        pr = pm.get_package_registry(parsed_args.registry_name)
        pb = pr.get_package_binary(settings_dict)
        pb.download_content(parsed_args.dir_path)

    def upload(self, *args):
        parser = argparse.ArgumentParser(prog="pacco binary upload")
        parser.add_argument("remote_name", help="remote name")
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("dir_path", help="directory to be uploaded")
        parser.add_argument("settings", help="settings for the specified registry "
                                             "(e.g. os=linux,version=2.1.0,type=debug")
        parsed_args = parser.parse_args(args)

        settings_value = Binary.__parse_settings_args(parsed_args.settings)
        pm = self.__rm.get_remote(parsed_args.remote_name)
        pr = pm.get_package_registry(parsed_args.registry_name)
        try:
            pr.get_package_binary(settings_value)
        except FileNotFoundError:
            pr.add_package_binary(settings_value)
        else:
            self.__out.writeln("WARNING: Existing binary found, overwriting")
        finally:
            pb = pr.get_package_binary(settings_value)
            pb.upload_content(parsed_args.dir_path)

    def remove(self, *args):
        parser = argparse.ArgumentParser(prog="pacco binary remove")
        parser.add_argument("remote_name", help="remote name")
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("settings", help="settings for the specified registry "
                                             "(e.g. os=linux,version=2.1.0,type=debug")
        parsed_args = parser.parse_args(args)

        settings_value = Binary.__parse_settings_args(parsed_args.settings)
        pm = self.__rm.get_remote(parsed_args.remote_name)
        pr = pm.get_package_registry(parsed_args.registry_name)
        pr.remove_package_binary(settings_value)


def main(args):
    CommandManager().run(*args)
