from __future__ import annotations
import os
from typing import Dict, Optional

from pacco.manager.file_based.package_manager import PackageManagerFileBased
from pacco.manager.interfaces.remote import RemoteInterface
from pacco.manager.utils.clients import LocalClient, NexusFileClient, FileBasedClientAbstract


class RemoteFileBased(RemoteInterface):
    def __init__(self, name: str, remote_type: str, client: FileBasedClientAbstract):
        self.client = client
        super(RemoteFileBased, self).__init__(name, remote_type, PackageManagerFileBased(client))

    @staticmethod
    def create(name: str, serialized: Dict[str, str]) -> RemoteInterface:
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
    def create(name: str, serialized: Dict[str, str], clean=False) -> LocalRemote:
        if 'path' not in serialized:
            serialized['path'] = ""
        return LocalRemote(name, serialized['remote_type'], serialized['path'], clean)

    def serialize(self) -> Dict[str, str]:
        return {'remote_type': 'local', 'path': self.__path}


class NexusSiteRemote(RemoteFileBased):
    url: str
    username: str
    password: str

    def __init__(self, name: str, remote_type: str, client: NexusFileClient):
        super(NexusSiteRemote, self).__init__(name, remote_type, client)

    @staticmethod
    def create(name: str, serialized: Dict[str, str], clean=False) -> NexusSiteRemote:
        client = NexusFileClient(serialized['url'], serialized['username'], serialized['password'], clean)
        remote_object = NexusSiteRemote(name, serialized['remote_type'], client)
        remote_object.url = serialized['url']
        remote_object.username = serialized['username']
        remote_object.password = serialized['password']
        return remote_object

    def serialize(self) -> Dict[str, str]:
        return {'remote_type': 'nexus_site', 'url': self.url,
                'username': self.username, 'password': self.password}
