import re

from pacco.cli.commands.utils.command_abstract import CommandAbstract
from pacco.manager.abstracts.remote import RemoteAbstract
from pacco.manager.abstracts.package_registry import PackageRegistryAbstract


class Registry(CommandAbstract):
    def list(self, *args):
        """
        List registries of a remote.
        """
        parser = self.init_parser('list')
        parser.add_argument("remote", help="remote name")
        parsed_args = parser.parse_args(args)
        pm = self.rm.get_remote(parsed_args.remote)
        self.out.writeln(pm.list_package_registries())

    def add(self, *args):
        """
        Add registry to remote.
        """
        parser = self.init_parser('add')
        parser.add_argument("remote", help="remote name")
        parser.add_argument("name", help="registry name")
        parser.add_argument("settings", help="settings key (e.g. os,version,obfuscation)")
        parsed_args = parser.parse_args(args)
        if not re.match(r"([(\w)-.]+,)*([(\w)-.]+),?", parsed_args.settings):
            raise ValueError("Settings must be in the form of ([(\\w)-.]+,)*([(\\w)-.]+),?")
        pm = self.rm.get_remote(parsed_args.remote)
        pm.add_package_registry(parsed_args.name, parsed_args.settings.split(","))

    def remove(self, *args):
        """
        Remove a registry from a specific remote.
        """
        parser = self.init_parser('remove')
        parser.add_argument("remote", help="remote name")
        parser.add_argument("name", help="registry name")
        parsed_args = parser.parse_args(args)
        pm = self.rm.get_remote(parsed_args.remote)
        pm.remove_package_registry(parsed_args.name)

    def binaries(self, *args):
        """
        List binaries of a registry from a specific remote.
        """
        parser = self.init_parser('binaries')
        parser.add_argument("remote", help="remote name")
        parser.add_argument("name", help="registry name")
        parsed_args = parser.parse_args(args)
        pm: RemoteAbstract = self.rm.get_remote(parsed_args.remote)
        pr: PackageRegistryAbstract = pm.get_package_registry(parsed_args.name)
        binaries = pr.list_package_binaries()
        serialized_binaries = []
        for binary in binaries:
            serialized_binaries.append(
                ",".join(sorted(
                    [
                        "{}={}".format(key, value)
                        for key, value in binary.items()
                    ]
                ))
            )
        self.out.writeln(sorted(serialized_binaries))

    def param_list(self, *args):
        """
        List params of a registry.
        """
        parser = self.init_parser('param_list')
        parser.add_argument("remote", help="remote name")
        parser.add_argument("name", help="registry name")

        parsed_args = parser.parse_args(args)
        pm = self.rm.get_remote(parsed_args.remote)
        pr = pm.get_package_registry(parsed_args.name)
        self.out.writeln(pr.param_list())

    def param_add(self, *args):
        """
        Add new parameter with default value to the binaries.
        """
        parser = self.init_parser('param_add')
        parser.add_argument("remote", help="remote name")
        parser.add_argument("name", help="registry name")
        parser.add_argument("param_name", help="the new param name to be added")
        parser.add_argument("default_value", help="the default_value assigned to the new param")

        parsed_args = parser.parse_args(args)
        pm = self.rm.get_remote(parsed_args.remote)
        pr = pm.get_package_registry(parsed_args.name)
        pr.param_add(parsed_args.param_name, parsed_args.default_value)

    def param_remove(self, *args):
        """
        Remove an existing parameter from all binaries.
        """
        parser = self.init_parser('param_remove')
        parser.add_argument("remote", help="remote name")
        parser.add_argument("name", help="registry name")
        parser.add_argument("param_name", help="the param name to be removed")

        parsed_args = parser.parse_args(args)
        pm = self.rm.get_remote(parsed_args.remote)
        pr = pm.get_package_registry(parsed_args.name)
        pr.param_remove(parsed_args.param_name)
