import argparse
import inspect
from typing import Dict, Callable

from pacco.cli import utils
from pacco.cli.output_stream import OutputStream
from pacco.manager.remote_manager import RemoteManager, ALLOWED_REMOTE_TYPES


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
        utils.show_help(self.__get_commands(), 'remote', self.__out)

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
