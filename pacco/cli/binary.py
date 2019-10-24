import argparse
import inspect
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Dict, Callable

from pacco.manager.utils.cache import Cache
from pacco.cli import utils
from pacco.manager.remote_manager import RemoteManager


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
        utils.show_help(self.__get_commands(), 'binary', self.__out)

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

        assignment = Binary.__parse_settings_args(parsed_args.settings)
        pm = self.__rm.get_remote(parsed_args.remote_name)
        pr = pm.get_package_registry(parsed_args.registry_name)
        try:
            pr.get_package_binary(assignment)
        except FileNotFoundError:
            pr.add_package_binary(assignment)
        else:
            self.__out.writeln("WARNING: Existing binary found, overwriting")
        finally:
            pb = pr.get_package_binary(assignment)
            pb.upload_content(parsed_args.dir_path)

    def remove(self, *args):
        parser = argparse.ArgumentParser(prog="pacco binary remove")
        parser.add_argument("remote_name", help="remote name")
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("settings", help="settings for the specified registry "
                                             "(e.g. os=linux,version=2.1.0,type=debug")
        parsed_args = parser.parse_args(args)

        assignment = Binary.__parse_settings_args(parsed_args.settings)
        pm = self.__rm.get_remote(parsed_args.remote_name)
        pr = pm.get_package_registry(parsed_args.registry_name)
        pr.remove_package_binary(assignment)

    def reassign(self, *args):
        """
        Change the assignment of a binary to a new one
        """
        parser = argparse.ArgumentParser(prog="pacco binary reassign")
        parser.add_argument("remote_name", help="remote name")
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("old_settings", help="old settings (e.g. os=linux,version=2.1.0,type=debug")
        parser.add_argument("new_settings", help="new settings (e.g. os=osx,version=2.1.1,type=debug")
        parsed_args = parser.parse_args(args)
        old_assignment = Binary.__parse_settings_args(parsed_args.old_settings)
        new_assignment = Binary.__parse_settings_args(parsed_args.new_settings)
        pm = self.__rm.get_remote(parsed_args.remote_name)
        pr = pm.get_package_registry(parsed_args.registry_name)
        pr.reassign_binary(old_assignment, new_assignment)

    def get_location(self, *args):
        parser = argparse.ArgumentParser(prog="pacco binary get_location")
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("settings", help="settings for the specified registry "
                                             "(e.g. os=linux,version=2.1.0,type=debug")
        parser.add_argument("--fresh_download", help="add this flag to not use local cache",
                            action="store_true")
        parsed_args = parser.parse_args(args)
        assignment = Binary.__parse_settings_args(parsed_args.settings)
        if not parsed_args.fresh_download:
            try:
                self.__out.write(Cache().get_path(parsed_args.registry_name, assignment))
                return
            except ValueError:
                logging.warning("The binary is not found in cache, will attemp fresh download")
        download_path = os.path.join(str(Path.home()), '.pacco_tmp')
        self.__rm.default_download(parsed_args.registry_name, assignment,
                                   download_path, fresh_download=parsed_args.fresh_download)
        shutil.rmtree(download_path)
        self.__out.write(Cache().get_path(parsed_args.registry_name, assignment))
