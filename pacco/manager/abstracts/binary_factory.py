from typing import Dict, Any

from pacco.manager.file_based.package_binary import PackageBinaryFileBased
from pacco.manager.abstracts.package_binary import PackageBinaryAbstract
from pacco.manager.file_based.utils.clients.abstract import FileBasedClientAbstract


def create_binary_object(registry_name: str, assignment: Dict[str, str], context: Any) -> PackageBinaryAbstract:
    if isinstance(context, FileBasedClientAbstract):
        return PackageBinaryFileBased(client=context, registry_name=registry_name, assignment=assignment)
    raise TypeError("Currently we only accept FileBasedClientAbstract instance as context")
