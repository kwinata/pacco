from typing import List, Optional

from nexuscli import nexus_config, nexus_client
from nexuscli.api.repository import collection

from pacco.manager.interfaces.package_manager import PackageManagerInterface


class PackageManagerNexus3(PackageManagerInterface):
    def __init__(self, url: str, username: str, password: str, repository_name: str, clean: Optional[bool] = False):
        config = nexus_config.NexusConfig(
            url=url,
            username=username,
            password=password,
        )
        client = nexus_client.NexusClient(config)
        repo_collection = collection.RepositoryCollection(client=client)
        self.repository_object = repo_collection.get_by_name(name=repository_name)
        super(PackageManagerNexus3, self).__init__()

    def list_package_registries(self) -> List[str]:
        raise NotImplementedError()

    def remove_package_registry(self, name: str) -> None:
        raise NotImplementedError()

    def add_package_registry(self, name: str, params: List[str]) -> None:
        raise NotImplementedError()

    def get_package_registry(self, name: str) -> PackageRegistryNexus3:
        raise NotImplementedError()
