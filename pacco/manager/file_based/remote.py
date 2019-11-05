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
    """
    client: FileBasedClientAbstract

    def __init__(self, configuration: Dict[str, str], clean: Optional[bool] = False):
        self.client = client_factory(configuration, clean)
        super(RemoteFileBased, self).__init__(configuration)

    def list_package_registries(self) -> List[str]:
        return sorted(self.client.ls())

    def remove_package_registry(self, name: str) -> None:
        self.client.rmdir(name)

    def allocate_space(self, name: str):
        self.client.mkdir(name)

    def get_registry_context(self, name: str):
        return self.client.dispatch_subdir(name)
