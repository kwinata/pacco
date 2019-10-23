from __future__ import annotations
import os
from typing import Dict, Optional

from pacco.client.clients import FileBasedClientAbstract, LocalClient, NexusFileClient
from pacco.manager.file_based.package_manager import PackageManagerFileBased


class RemoteFileBased:
    package_manager: PackageManagerFileBased = None

    def __init__(self, name: str, remote_type: str, client: FileBasedClientAbstract):
        self.name = name
        self.remote_type = remote_type
        self.package_manager = PackageManagerFileBased(client)

    def __str__(self):
        return "[{}, {}]".format(self.name, self.remote_type)

    @staticmethod
    def create(name: str, serialized: Dict[str, str]) -> RemoteFileBased:
        raise NotImplementedError()

    def serialize(self) -> Dict[str, str]:
        raise NotImplementedError()


class LocalRemote(RemoteFileBased):
    def __init__(self, name: str, remote_type: str, path: Optional[str] = "", clean: Optional[bool] = False):
        if path:
            self.__path = os.path.abspath(path)
        else:
            self.__path = ""
        client = LocalClient(self.__path, clean)
        super(LocalRemote, self).__init__(name, remote_type, client)

    @staticmethod
    def create(name: str, serialized: Dict[str, str]) -> LocalRemote:
        if 'path' not in serialized:
            serialized['path'] = ""
        return LocalRemote(name, serialized['remote_type'], serialized['path'])

    def serialize(self) -> Dict[str, str]:
        return {'remote_type': 'local', 'path': self.__path}


class NexusSiteRemote(RemoteFileBased):
    url: str
    username: str
    password: str

    def __init__(self, name: str, remote_type: str, client: NexusFileClient):
        super(NexusSiteRemote, self).__init__(name, remote_type, client)

    @staticmethod
    def create(name: str, serialized: Dict[str, str]) -> NexusSiteRemote:
        client = NexusFileClient(serialized['url'], serialized['username'], serialized['password'])
        remote_object = NexusSiteRemote(name, serialized['remote_type'], client)
        remote_object.url = serialized['url']
        remote_object.username = serialized['username']
        remote_object.password = serialized['password']
        return remote_object

    def serialize(self) -> Dict[str, str]:
        return {'remote_type': 'nexus_site', 'url': self.url,
                'username': self.username, 'password': self.password}
