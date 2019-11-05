from typing import Optional, List

from pacco.manager.file_based.package_registry import PackageRegistryFileBased
from pacco.manager.abstracts.package_registry import PackageRegistryAbstract
from pacco.manager.file_based.utils.clients.abstract import FileBasedClientAbstract


def create_registry_object(name: str, params: Optional[List[str]] = None, context: Optional[object] = None) -> \
        PackageRegistryAbstract:
    if isinstance(context, FileBasedClientAbstract):
        return PackageRegistryFileBased(name, client=context, params=params)
    raise TypeError("Currently we only accept FileBasedClientAbstract instance as context")
