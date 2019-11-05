import random
import re
import string

from typing import Optional, List, Dict, Callable

from pacco.manager.utils.clients.abstract import FileBasedClientAbstract
from pacco.manager.file_based.package_binary import PackageBinaryFileBased
from pacco.manager.interfaces.package_registry import PackageRegistryInterface


class PackageRegistryFileBased(PackageRegistryInterface):
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

    def initialize_remote_params(self, params: List[str]):
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

    def __get_serialized_assignment_to_wrapper_mapping(self):
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

    def __rename_serialized_assignment(self, action: Callable[[Dict[str, str]], None]):
        for serialized_assignment, dir_name in self.__get_serialized_assignment_to_wrapper_mapping().items():
            assignment = PackageRegistryFileBased.__unserialize_assignment(serialized_assignment)
            action(assignment)
            new_serialized_assignment = PackageRegistryFileBased.__serialize_assignment(assignment)

            sub_client = self.client.dispatch_subdir(dir_name)
            sub_client.mkdir(new_serialized_assignment)
            sub_client.rmdir(serialized_assignment)

    def param_list(self) -> List[str]:
        return self.params

    def param_add(self, name: str, default_value: Optional[str] = "default") -> None:
        if name in self.params:
            raise ValueError("{} already in params".format(name))

        self.client.rmdir(self.__serialize_params(self.params))
        self.params.append(name)
        self.client.mkdir(self.__serialize_params(self.params))

        self.__rename_serialized_assignment(lambda x: x.update({name: default_value}))

    def param_remove(self, name: str) -> None:
        if name not in self.params:
            raise ValueError("{} not in params".format(name))

        new_set_of_serialized_assignment = set()
        for serialized_assignment, dir_name in self.__get_serialized_assignment_to_wrapper_mapping().items():
            assignment = PackageRegistryFileBased.__unserialize_assignment(serialized_assignment)
            del assignment[name]
            new_serialized_assignment = PackageRegistryFileBased.__serialize_assignment(assignment)
            if new_serialized_assignment in new_set_of_serialized_assignment:
                raise NameError("Cannot remove parameter {} since it will cause "
                                "two binary to have the same value".format(name))
            else:
                new_set_of_serialized_assignment.add(new_serialized_assignment)

        self.client.rmdir(self.__serialize_params(self.params))
        self.params.remove(name)
        self.client.mkdir(self.__serialize_params(self.params))

        self.__rename_serialized_assignment(lambda x: x.pop(name))

    def reassign_binary(self, old_assignment: Dict[str, str], new_assignment: Dict[str, str]) -> None:
        if set(new_assignment.keys()) != set(self.params):
            raise KeyError("wrong settings key: {} is not {}".format(sorted(new_assignment.keys()),
                                                                     sorted(self.params)))

        serialized_old_assignment = PackageRegistryFileBased.__serialize_assignment(old_assignment)
        serialized_new_assignment = PackageRegistryFileBased.__serialize_assignment(new_assignment)
        mapping = self.__get_serialized_assignment_to_wrapper_mapping()
        if serialized_old_assignment not in mapping:
            raise ValueError("there is no binary that match the assignment")
        if serialized_new_assignment in mapping:
            raise NameError("there already exist binary with same assignment with the new one")

        sub_client = self.client.dispatch_subdir(mapping[serialized_old_assignment])
        sub_client.rmdir(serialized_old_assignment)
        sub_client.mkdir(serialized_new_assignment)
