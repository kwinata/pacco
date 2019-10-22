from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from pacco.classes_interface import PackageManager
from pacco.classes_file_based import PackageManagerFileBased
from pacco.clients import LocalClient, NexusFileClient, FileBasedClientAbstract


ALLOWED_REMOTE_TYPES = [
    'local',
    'nexus_site',
]

DEFAULT_REMOTE_NAME = 'default'


class RemoteManager:
    """
    Function to manage ``.pacco_config`` file as the storage for remote lists
    With ``RemoteManager``, you can manage multiple ``PackageManager`` s

    Examples:
        >>> open(os.path.join(str(Path.home()), ".pacco_config"), "w").close()
        >>> os.remove(os.path.join(str(Path.home()), ".pacco_config"))
        >>> rm = RemoteManager()
        >>> rm.add_remote('local_test', {'remote_type':'local'})
        >>> rm.list_remote()
        ['local_test']
        >>> rm.add_remote('local_test_2', {'remote_type':'local', 'path': 'storage'})
        >>> sorted(rm.list_remote())
        ['local_test', 'local_test_2']
        >>> rm.set_default(['local_test_2', 'local_test'])
        >>> rm.get_default()
        ['local_test_2', 'local_test']
        >>> rm.remove_remote('local_test')
        Traceback (most recent call last):
        ...
        ValueError: The remote local_test is still in default remote, remove it first
        >>> rm.set_default(['local_test_2'])
        >>> rm.remove_remote('local_test')
        >>> del rm  # auto save
        >>> other_rm = RemoteManager()
        >>> other_rm.list_remote()
        ['local_test_2']
        >>> other_rm.get_remote('local_test_2')
        PackageManagerObject
    """

    def __init__(self):
        self.__pacco_config = os.path.join(str(Path.home()), '.pacco_config')
        if not os.path.exists(self.__pacco_config):
            self.remotes = {}
            self.default_remotes = []

        else:
            with open(self.__pacco_config, "r") as f:
                pacco_config = yaml.load(f, Loader=yaml.Loader)

            remotes_serialized = pacco_config['remotes']
            default_remotes = pacco_config['default']

            remotes = {name: RemoteManager.__instantiate_remote(name, remotes_serialized[name])
                       for name in remotes_serialized}

            self.remotes = remotes
            self.default_remotes = default_remotes

    def __del__(self):
        self.save()

    def save(self) -> None:
        """
        Save the current state to ".pacco_config", this will also be done in the ``__del__``
        method, such that even if you forget to save, it will be auto saved when the program closes.
        """
        serialized_remotes = {name: self.remotes[name].serialize() for name in self.remotes}
        with open(self.__pacco_config, "w") as f:
            yaml.dump({'remotes': serialized_remotes, 'default': self.default_remotes}, stream=f)

    @staticmethod
    def __instantiate_remote(name: str, serialized):
        if serialized['remote_type'] == 'local':
            return _LocalRemote.create(name, serialized)
        elif serialized['remote_type'] == 'nexus_site':
            return _NexusSiteRemote.create(name, serialized)
        else:
            raise ValueError("The remote_type {} is not supported, currently only supports [{}]".format(
                serialized['remote_type'], ", ".join(['local', 'nexus_site'])
            ))

    def get_remote(self, name: str) -> PackageManager:
        """
        Get the ``PackageManager`` based on the remote name.

        Args:
            name: the name of the remote
        Return:
            the package manager object
        """
        if name not in self.remotes:
            raise KeyError("The remote named {} is not found".format(name))
        return self.remotes[name].package_manager

    def list_remote(self) -> List[str]:
        """
        Get the list of the remote names
        """
        return list(self.remotes.keys())

    def add_remote(self, name: str, configuration: Dict[str, str]) -> None:
        """
        Add/register a new remote. Currently there is two possible configuration:

        Local client: ::

            {
                'remote_type': 'local',
                'path': '[PATH]', (optional, will use ~/.pacco/ if not declared)
            }

        Nexus site client: ::

            {
                'remote_type': 'nexus_site',
                'url': '[URL]',
                'username': '[USERNAME]',
                'password': '[PASSWORD]',
            }

        Args:
            name: the name of the new remote
            configuration: a dictionary of the configuration as described above.
        """
        if name in self.list_remote():
            raise NameError("The remote with name {} already exists".format(name))
        self.remotes[name] = RemoteManager.__instantiate_remote(name, configuration)

    def remove_remote(self, name: str) -> None:
        """
        De-register a remote from this remote manager.

        Args:
            name: the name of the remote to be de-registered
        """
        if name in self.default_remotes:
            raise ValueError("The remote {} is still in default remote, remove it first".format(name))
        if name not in self.remotes:
            raise KeyError("The remote {} is not registered".format(name))
        del self.remotes[name]

    def get_default(self) -> List[str]:
        """
        Get the list of the default remotes to be used in the default download

        Returns:
            the list of remotes in order to be tried. (index 0 will be tried first)
        """
        return list(self.default_remotes)

    def set_default(self, remotes: List[str]) -> None:
        """
        Set the default remote list as the "try list" for the default download

        Args:
            remotes: list of the remote names
        Exception:
            KeyError: when the Remote name does not exists
        """
        for remote in remotes:
            if remote not in self.remotes:
                raise KeyError("remote {} does not exist".format(remote))
        self.default_remotes = remotes

    def default_download(self, package_name: str, assignment: Dict[str, str], dir_path: str) -> None:
        """
        Try to download a package binary from the remotes in the default remote list.

        Args:
            package_name: package registry name of the binary
            assignment: the dictionary of the binary configuration
            dir_path: the download destination
        Examples:
            >>> import os
            >>> __ = os.system("rm -f ~/.pacco_config")
            >>> __ = os.system('rm -rf download_folder download_folder2 local3 pacco_storage tempfolder ~/.pacco')
            >>> rm = RemoteManager()
            >>> rm.add_remote('local', {'remote_type': 'local'})
            >>> pm = rm.get_remote('local')
            >>> pm.add_package_registry('openssl', ['os'])
            >>> pr = pm.get_package_registry('openssl')
            >>> pr.add_package_binary({'os': 'osx'})
            >>> pb = pr.get_package_binary({'os': 'osx'})
            >>> os.makedirs('tempfolder')
            >>> open("tempfolder/testfile", "w").close()
            >>> pb.upload_content('tempfolder')
            >>> rm.add_remote('local2', {'remote_type': 'local', 'path': 'pacco_storage'})
            >>> pm2 = rm.get_remote('local2')
            >>> pm2.add_package_registry('openssl', ['os'])
            >>> rm.add_remote('local3', {'remote_type': 'local', 'path': 'local3'})
            >>> rm.set_default(['local2', 'local3', 'local'])
            >>> rm.default_download('openssl', {'os': 'osx'}, 'download_folder')
            >>> os.listdir('download_folder')
            ['testfile']
            >>> rm.set_default(['local', 'local3'])
            >>> rm.default_download('openssl', {'os': 'osx'}, 'download_folder2')
            >>> os.listdir('download_folder2')
            ['testfile']
            >>> rm.set_default(['local3'])
            >>> rm.default_download('openssl', {'os': 'osx'}, 'download_folder3')
            Traceback (most recent call last):
            ...
            FileNotFoundError: Such binary does not exist in any remotes in the default remote list
            >>> __ = os.system('rm -rf download_folder download_folder2 local3 pacco_storage tempfolder ~/.pacco')
        """
        for remote_name in self.default_remotes:
            remote = self.get_remote(remote_name)
            if package_name in remote.list_package_registries():
                pr = remote.get_package_registry(package_name)
                try:
                    pb = pr.get_package_binary(assignment)
                except (KeyError, FileNotFoundError):
                    continue
                else:
                    pb.download_content(dir_path)
                    return
        raise FileNotFoundError("Such binary does not exist in any remotes in the default remote list")


class _RemoteFileBased:
    package_manager: PackageManagerFileBased = None

    def __init__(self, name: str, remote_type: str, client: FileBasedClientAbstract):
        self.name = name
        self.remote_type = remote_type
        self.package_manager = PackageManagerFileBased(client)

    def __str__(self):
        return "[{}, {}]".format(self.name, self.remote_type)

    @staticmethod
    def create(name: str, serialized: Dict[str, str]) -> _RemoteFileBased:
        raise NotImplementedError()

    def serialize(self) -> Dict[str, str]:
        raise NotImplementedError()


class _LocalRemote(_RemoteFileBased):
    def __init__(self, name: str, remote_type: str, path: Optional[str] = "", clean: Optional[bool] = False):
        if path:
            self.__path = os.path.abspath(path)
        else:
            self.__path = ""
        client = LocalClient(self.__path, clean)
        super(_LocalRemote, self).__init__(name, remote_type, client)

    @staticmethod
    def create(name: str, serialized: Dict[str, str]) -> _LocalRemote:
        if 'path' not in serialized:
            serialized['path'] = ""
        return _LocalRemote(name, serialized['remote_type'], serialized['path'])

    def serialize(self) -> Dict[str, str]:
        return {'remote_type': 'local', 'path': self.__path}


class _NexusSiteRemote(_RemoteFileBased):
    def __init__(self, name: str, remote_type: str, url: str, username: str, password: str,
                 clean: Optional[bool] = False):
        self.__url = url
        self.__username = username
        self.__password = password
        client = NexusFileClient(url, username, password, clean)
        super(_NexusSiteRemote, self).__init__(name, remote_type, client)

    @staticmethod
    def create(name: str, serialized: Dict[str, str]) -> _NexusSiteRemote:
        return _NexusSiteRemote(name, serialized['remote_type'], serialized['url'],
                                serialized['username'], serialized['password'])

    def serialize(self) -> Dict[str, str]:
        return {'remote_type': 'nexus_site', 'url': self.__url,
                'username': self.__username, 'password': self.__password}
