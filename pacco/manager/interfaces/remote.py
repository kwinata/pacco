from __future__ import annotations
from typing import Dict


class RemoteAbstract:
    name: str
    remote_type: str

    def __str__(self):
        return "[{}, {}]".format(self.name, self.remote_type)

    @staticmethod
    def create(name: str, serialized: Dict[str, str]) -> RemoteAbstract:
        raise NotImplementedError()

    def serialize(self) -> Dict[str, str]:
        raise NotImplementedError()
