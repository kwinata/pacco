import random
import re
import string

from typing import Optional, List, Dict

from pacco.manager.file_based.utils.clients.abstract import FileBasedClientAbstract
from pacco.manager.abstracts.package_registry import PackageRegistryAbstract


class PackageRegistryFileBased(PackageRegistryAbstract):
    """
    An implementation of the PackageRegistry interface
    """
    __params_prefix = '__params'

    def __init__(self, name: str, client: FileBasedClientAbstract, params: Optional[List[str]] = None):
        if not isinstance(client, FileBasedClientAbstract):
            raise TypeError("Must be using FileBasedClient")
        self.client = client
        super(PackageRegistryFileBased, self).__init__(name, params)

    def get_remote_params(self) -> Optional[List[str]]:
        params = None
        dirs = self.client.ls()
        for dir_name in dirs:
            if PackageRegistryFileBased.__params_prefix in dir_name:
                params = dir_name.split('==')[1:]
        return params

    def initialize_remote_params(self, params: List[str]) -> None:
        self.client.mkdir(self.__serialize_params(self.params))

    @staticmethod
    def __serialize_params(params: List[str]) -> str:
        params = sorted(params)
        return '=='.join([PackageRegistryFileBased.__params_prefix] + params)

    @staticmethod
    def __serialize_assignment(assignment: Dict[str, str]) -> str:
        for key, value in assignment.items():
            if len(value) == 0:
                raise ValueError("assignment value for param {} cannot be an empty string".format(key))
        sorted_assignment_tuple = sorted(assignment.items(), key=lambda x: x[0])
        zipped_assignment = ['='.join(pair) for pair in sorted_assignment_tuple]
        return '=='.join(zipped_assignment)

    @staticmethod
    def __unserialize_assignment(dir_name: str) -> Dict[str, str]:
        if not re.match(r"((\w+=\w+)==)*(\w+=\w+)", dir_name):
            raise ValueError("Invalid dir_name syntax {}".format(dir_name))
        return {arg.split('=')[0]: arg.split('=')[1] for arg in dir_name.split('==')}

    def __get_serialized_assignment_to_wrapper_mapping(self) -> Dict[str, str]:
        dir_names = self.client.ls()
        dir_names.remove(self.__serialize_params(self.params))

        mapping = {}
        for dir_name in dir_names:
            sub_dirs = self.client.dispatch_subdir(dir_name).ls()
            if 'bin' in sub_dirs:
                sub_dirs.remove('bin')
            serialized_assignment = sub_dirs[0]
            mapping[serialized_assignment] = dir_name

        return mapping

    def list_package_binaries(self) -> List[Dict[str, str]]:
        return [PackageRegistryFileBased.__unserialize_assignment(serialized_assignment)
                for serialized_assignment in self.__get_serialized_assignment_to_wrapper_mapping()]

    @staticmethod
    def __random_string(length: int) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def allocate_space_for_binary(self, assignment: Dict[str, str]) -> None:
        serialized_assignment = PackageRegistryFileBased.__serialize_assignment(assignment)
        mapping = self.__get_serialized_assignment_to_wrapper_mapping()

        new_random_dir_name = PackageRegistryFileBased.__random_string(10)
        if new_random_dir_name in mapping.values():
            new_random_dir_name = PackageRegistryFileBased.__random_string(10)

        self.client.mkdir(new_random_dir_name)
        self.client.dispatch_subdir(new_random_dir_name).mkdir(serialized_assignment)
        return

    def remove_package_binary(self, assignment: Dict[str, str]):
        self.client.rmdir(self.__get_serialized_assignment_to_wrapper_mapping()[
                              PackageRegistryFileBased.__serialize_assignment(assignment)
                          ])

    def get_binary_context(self, assignment: Dict[str, str]):
        serialized_assignment = PackageRegistryFileBased.__serialize_assignment(assignment)
        return self.client.dispatch_subdir(
            self.__get_serialized_assignment_to_wrapper_mapping()[serialized_assignment]
        )

    def reset_remote_params(self, old_params: List[str], new_params: List[str]):
        self.client.mkdir(self.__serialize_params(new_params))
        self.client.rmdir(self.__serialize_params(old_params))

    def reset_binary_assignment(self, assignment: Dict[str, str], new_assignment: Dict[str, str]):
        sub_client = self.client.dispatch_subdir(
            self.__get_serialized_assignment_to_wrapper_mapping()[PackageRegistryFileBased.__serialize_assignment(
                assignment
            )]
        )
        sub_client.mkdir(PackageRegistryFileBased.__serialize_assignment(new_assignment))
        sub_client.rmdir(PackageRegistryFileBased.__serialize_assignment(assignment))
