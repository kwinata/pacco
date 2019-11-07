import logging
import os
import re
import shutil
from pathlib import Path
from typing import Dict

from pacco.cli.commands.utils.command_abstract import CommandAbstract
from pacco.manager.abstracts.package_binary import PackageBinaryAbstract
from pacco.manager.abstracts.remote import RemoteAbstract
from pacco.manager.abstracts.package_registry import PackageRegistryAbstract
from pacco.manager.utils.cache import Cache


class Binary(CommandAbstract):
    @staticmethod
    def __parse_settings_args(settings_args: str) -> Dict[str, str]:
        if not re.match(r"([\w\-.]+=[\w\-.]+,)*([\w\-.]+=[\w\-.]+),?", settings_args):
            raise ValueError("The settings configuration must match ([\\w-.]+=[\\w-.]+,)*([\\w-.]+=[\\w-.]+),?")
        return {token.split('=')[0]: token.split('=')[1] for token in settings_args.split(',')}

    def download(self, *args):
        parser = self.init_parser('download')
        parser.add_argument("remote_name", help="remote name")
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("dir_path", help="download path")
        parser.add_argument("settings", help="settings for the specified registry "
                                             "(e.g. os=linux,version=2.1.0,type=debug")
        parsed_args = parser.parse_args(args)

        settings_dict = Binary.__parse_settings_args(parsed_args.settings)
        if parsed_args.remote_name == 'default':
            self.rm.default_download(parsed_args.registry_name, settings_dict, parsed_args.dir_path)
        pm: RemoteAbstract = self.rm.get_remote(parsed_args.remote_name)
        pr: PackageRegistryAbstract = pm.get_package_registry(parsed_args.registry_name)
        pb: PackageBinaryAbstract = pr.get_package_binary(settings_dict)
        pb.download_content(parsed_args.dir_path)

    def upload(self, *args):
        parser = self.init_parser('upload')
        parser.add_argument("remote_name", help="remote name")
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("dir_path", help="directory to be uploaded")
        parser.add_argument("settings", help="settings for the specified registry "
                                             "(e.g. os=linux,version=2.1.0,type=debug")
        parsed_args = parser.parse_args(args)

        assignment = Binary.__parse_settings_args(parsed_args.settings)
        pm: RemoteAbstract = self.rm.get_remote(parsed_args.remote_name)
        pr = pm.get_package_registry(parsed_args.registry_name)
        try:
            pr.get_package_binary(assignment)
        except FileNotFoundError:
            pr.add_package_binary(assignment)
        else:
            self.out.writeln("WARNING: Existing binary found, overwriting")
        finally:
            pb = pr.get_package_binary(assignment)
            pb.upload_content(parsed_args.dir_path)

    def remove(self, *args):
        parser = self.init_parser('remove')
        parser.add_argument("remote_name", help="remote name")
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("settings", help="settings for the specified registry "
                                             "(e.g. os=linux,version=2.1.0,type=debug")
        parsed_args = parser.parse_args(args)

        assignment = Binary.__parse_settings_args(parsed_args.settings)
        pm = self.rm.get_remote(parsed_args.remote_name)
        pr = pm.get_package_registry(parsed_args.registry_name)
        pr.remove_package_binary(assignment)

    def reassign(self, *args):
        """
        Change the assignment of a binary to a new one
        """
        parser = self.init_parser('reassign')
        parser.add_argument("remote_name", help="remote name")
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("old_settings", help="old settings (e.g. os=linux,version=2.1.0,type=debug")
        parser.add_argument("new_settings", help="new settings (e.g. os=osx,version=2.1.1,type=debug")
        parsed_args = parser.parse_args(args)
        old_assignment = Binary.__parse_settings_args(parsed_args.old_settings)
        new_assignment = Binary.__parse_settings_args(parsed_args.new_settings)
        pm = self.rm.get_remote(parsed_args.remote_name)
        pr = pm.get_package_registry(parsed_args.registry_name)
        pr.reassign_binary(old_assignment, new_assignment)

    def get_location(self, *args):
        parser = self.init_parser('get_location')
        parser.add_argument("registry_name", help="registry name")
        parser.add_argument("settings", help="settings for the specified registry "
                                             "(e.g. os=linux,version=2.1.0,type=debug")
        parser.add_argument("--fresh_download", help="add this flag to not use local cache",
                            action="store_true")
        parsed_args = parser.parse_args(args)
        assignment = Binary.__parse_settings_args(parsed_args.settings)
        if not parsed_args.fresh_download:
            try:
                self.out.write(Cache().get_path(parsed_args.registry_name, assignment))
                return
            except ValueError:
                logging.info("The binary is not found in cache, will attemp fresh download")
        del assignment['__pacco_registry_name']
        download_path = os.path.join(str(Path.home()), '.pacco_tmp')
        self.rm.default_download(parsed_args.registry_name, assignment,
                                 download_path, fresh_download=parsed_args.fresh_download)
        shutil.rmtree(download_path)
        self.out.write(Cache().get_path(parsed_args.registry_name, assignment))
