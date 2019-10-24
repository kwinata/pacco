from pacco.cli.commands.utils.command_abstract import CommandAbstract
from pacco.manager.remote_manager import ALLOWED_REMOTE_TYPES


class Remote(CommandAbstract):
    def list(self, *args):
        """
        List existing remotes.
        """
        parser = self.init_parser('list')
        parser.parse_args(args)
        remotes = self.rm.list_remote()
        self.out.writeln(remotes)

    def add(self, *args):
        """
        Add a remote.
        """
        parser = self.init_parser('add')
        parser.add_argument("name", help="remote name")
        parser.add_argument("type", help="remote type", choices=ALLOWED_REMOTE_TYPES)
        parsed_args = parser.parse_args(args)
        if parsed_args.type == "local":
            path = input("Path (if empty, ~/.pacco/ will be used): ")
            self.rm.add_remote(parsed_args.name, {
                "remote_type": "local",
                "path": path
            })
        elif parsed_args.type == "nexus_site":
            url = input("URL: ")
            username = input("Username: ")
            from getpass import getpass
            password = getpass()
            self.rm.add_remote(parsed_args.name, {
                "remote_type": "nexus_site",
                "url": url,
                "username": username,
                "password": password
            })

    def remove(self, *args):
        """
        Remove a remote.
        """
        parser = self.init_parser('remove')
        parser.add_argument("name", help="remote name")
        parsed_args = parser.parse_args(args)
        self.rm.remove_remote(parsed_args.name)

    def set_default(self, *args):
        """
        Set default remote(s).
        """
        parser = self.init_parser('set_default')
        parser.add_argument("name", nargs="*", help="remote name")
        parsed_args = parser.parse_args(args)
        self.rm.set_default(parsed_args.name)

    def list_default(self, *args):
        """
        List default remote(s).
        """
        parser = self.init_parser('list_default')
        parser.parse_args(args)
        default_remotes = self.rm.get_default()
        self.out.writeln(default_remotes)
