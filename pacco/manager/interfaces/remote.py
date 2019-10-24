from __future__ import annotations
from typing import Dict

from pacco.manager.interfaces.package_manager import PackageManagerInterface


class RemoteInterface:
    def __init__(self, name: str, remote_type: str, package_manager: PackageManagerInterface):
        self.name = name
        self.remote_type = remote_type
        self.package_manager = package_manager

    def __str__(self):
        return "[{}, {}]".format(self.name, self.remote_type)

    @staticmethod
    def create(name: str, serialized: Dict[str, str]) -> RemoteInterface:
        raise NotImplementedError()

    def serialize(self) -> Dict[str, str]:
        raise NotImplementedError()
