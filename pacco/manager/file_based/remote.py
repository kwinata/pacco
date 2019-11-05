from typing import List, Dict, Optional

from pacco.manager.utils.clients.abstract import FileBasedClientAbstract
from pacco.manager.file_based.package_registry import PackageRegistryFileBased
from pacco.manager.interfaces.remote import RemoteInterface
from pacco.manager.utils.clients.local import LocalClient
from pacco.manager.utils.clients.nexus import NexusFileClient
from pacco.manager.utils.clients.webdav import WebDavClient


def client_factory(configuration, clean):
    if configuration['remote_type'] == 'local':
        if 'path' not in configuration:
            configuration['path'] = ''
        return LocalClient(path=configuration['path'], clean=clean)
    elif configuration['remote_type'] == 'nexus_site':
        return NexusFileClient(
            url=configuration['url'],
            username=configuration['username'],
            password=configuration['password'],
            clean=clean,
        )
    elif configuration['remote_type'] == 'webdav':
        return WebDavClient(
            host_path=configuration['host_path'],
            credential=configuration['credential'],
            clean=clean,
        )


class RemoteFileBased(RemoteInterface):
    """
    An implementation of the Remote interface

    Examples:
        >>> from pacco.manager.utils.clients.local import LocalClient
        >>> from pacco.manager.utils.clients.nexus import NexusFileClient
        >>> client = LocalClient(clean=True)
        >>> import os
        >>> if 'NEXUS_URL' in os.environ:
        ...     client = NexusFileClient(os.environ['NEXUS_URL'], 'admin', 'admin123', clean=True)
        ...
        >>> pm = RemoteFileBased(client)
        >>> pm.list_package_registries()
        []
        >>> pm.add_package_registry('openssl', ['os', 'compiler', 'version'])
        >>> pm.add_package_registry('boost', ['os', 'target', 'type'])
        >>> pm.add_package_registry('openssl', ['os', 'compiler', 'version'])
        Traceback (most recent call last):
            ...
        FileExistsError: The package registry openssl is already found
        >>> pm.list_package_registries()
        ['boost', 'openssl']
        >>> pm.remove_package_registry('openssl')
        >>> pm.list_package_registries()
        ['boost']
        >>> pm.get_package_registry('boost')
        PR[boost, os, target, type]
    """
    client: FileBasedClientAbstract

    def __init__(self, configuration: Dict[str, str], clean: Optional[bool] = False):
        self.client = client_factory(configuration, clean)
        super(RemoteFileBased, self).__init__(configuration)

    def list_package_registries(self) -> List[str]:
        return sorted(self.client.ls())

    def remove_package_registry(self, name: str) -> None:
        self.client.rmdir(name)

    def add_package_registry(self, name: str, params: List[str]) -> None:
        dirs = self.client.ls()
        if name in dirs:
            raise FileExistsError("The package registry {} is already found".format(name))
        self.client.mkdir(name)
        PackageRegistryFileBased(name, self.client.dispatch_subdir(name), params)
        return

    def get_package_registry(self, name: str) -> PackageRegistryFileBased:
        dirs = self.client.ls()
        if name not in dirs:
            raise FileNotFoundError("The package registry {} is not found".format(name))
        return PackageRegistryFileBased(name, self.client.dispatch_subdir(name))
