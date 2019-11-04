from typing import Optional, List, Dict

from pacco.manager.interfaces.package_registry import PackageRegistryInterface


class PackageRegistryNexus3(PackageRegistryInterface):
    def __init__(self, name: str, params: Optional[List[str]] = None):
        self.name = name
        self.params = params

    def list_package_binaries(self) -> List[Dict[str, str]]:
        raise NotImplementedError()

    def add_package_binary(self, assignment: Dict[str, str]) -> None:
        raise NotImplementedError()

    def remove_package_binary(self, assignment: Dict[str, str]):
        raise NotImplementedError()

    def get_package_binary(self, assignment: Dict[str, str]) -> PackageBinaryNexus3:
        raise NotImplementedError()

    def param_list(self) -> List[str]:
        raise NotImplementedError()

    def param_add(self, name: str, default_value: Optional[str] = "default") -> None:
        raise NotImplementedError()

    def param_remove(self, name: str) -> None:
        raise NotImplementedError()

    def reassign_binary(self, old_assignment: Dict[str, str], new_assignment: Dict[str, str]) -> None:
        raise NotImplementedError()
