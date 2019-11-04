from __future__ import annotations
from typing import Dict

from pacco.manager.interfaces.remote import RemoteInterface
from pacco.manager.nexus3.package_manager import PackageManagerNexus3


class Nexus3Remote(RemoteInterface):
    def __init__(self, name: str, remote_type: str, package_manager: PackageManagerNexus3):
        pass

    def __str__(self):
        return "[{}, {}]".format(self.name, self.remote_type)

    @staticmethod
    def create(name: str, serialized: Dict[str, str]) -> Nexus3Remote:
        raise NotImplementedError()

    def serialize(self) -> Dict[str, str]:
        raise NotImplementedError()
