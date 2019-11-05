from typing import Optional, List

from pacco.manager.file_based.package_registry import PackageRegistryFileBased
from pacco.manager.utils.clients.abstract import FileBasedClientAbstract


def create_registry(name: str, params: Optional[List[str]] = None, context: Optional[object] = None):
    if isinstance(context, FileBasedClientAbstract):
        return PackageRegistryFileBased(name, client=context, params=params)
    raise TypeError("Currently we only accept FileBasedClientAbstract instance as context")
