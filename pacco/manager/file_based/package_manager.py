from typing import List

from pacco.manager.utils.clients import FileBasedClientAbstract
from pacco.manager.file_based.package_registry import PackageRegistryFileBased
from pacco.manager.interfaces.package_manager import PackageManagerInterface


class PackageManagerFileBased(PackageManagerInterface):
    """
    An implementation of the PackageManager interface

    Examples:
        >>> from pacco.manager.utils.clients import LocalClient, NexusFileClient
        >>> client = LocalClient(clean=True)
        >>> import os
        >>> if 'NEXUS_URL' in os.environ: client = NexusFileClient(os.environ['NEXUS_URL'], 'admin', 'admin123', clean=True)
        >>> pm = PackageManagerFileBased(client)
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

    def __init__(self, client: FileBasedClientAbstract):
        if not isinstance(client, FileBasedClientAbstract):
            raise TypeError("Must be using FileBasedClient")
        self.client = client
        super(PackageManagerFileBased, self).__init__()

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

    def __repr__(self):
        return "PackageManagerObject"
