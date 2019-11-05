from typing import List, Dict, Optional

from pacco.manager.file_based.utils.clients.client_factory import create_client_object
from pacco.manager.file_based.utils.clients.abstract import FileBasedClientAbstract
from pacco.manager.abstracts.remote import RemoteAbstract


class RemoteFileBased(RemoteAbstract):
    """
    An implementation of the Remote interface
    """
    client: FileBasedClientAbstract

    def __init__(self, configuration: Dict[str, str], clean: Optional[bool] = False):
        self.client = create_client_object(configuration, clean)
        super(RemoteFileBased, self).__init__(configuration)

    def list_package_registries(self) -> List[str]:
        return sorted(self.client.ls())

    def remove_package_registry(self, name: str) -> None:
        self.client.rmdir(name)

    def allocate_space(self, name: str):
        self.client.mkdir(name)

    def get_registry_context(self, name: str):
        return self.client.dispatch_subdir(name)
