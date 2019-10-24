import random
import re
import string

from typing import Optional, List, Dict, Callable

from pacco.manager.utils.clients import FileBasedClientAbstract
from pacco.manager.file_based.package_binary import PackageBinaryFileBased
from pacco.manager.interfaces.package_registry import PackageRegistryInterface


class PackageRegistryFileBased(PackageRegistryInterface):
    """
    An implementation of the PackageRegistry interface

    Examples:
        >>> from pacco.manager.utils.clients import LocalClient, NexusFileClient
        >>> client = LocalClient(clean=True)
        >>> import os
        >>> if 'NEXUS_URL' in os.environ: client = NexusFileClient(os.environ['NEXUS_URL'], 'admin', 'admin123', clean=True)
        >>> from pacco.manager.file_based.package_manager import PackageManagerFileBased
        >>> pm = PackageManagerFileBased(client)
        >>> pm.add_package_registry('openssl', ['os', 'compiler', 'version'])
        >>> pr = pm.get_package_registry('openssl')
        >>> pr.list_package_binaries()
        []
        >>> pr.add_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})
        >>> pr.add_package_binary({'host_os':'osx', 'compiler':'clang', 'version':'1.0'})
        Traceback (most recent call last):
            ...
        KeyError: "wrong settings key: ['compiler', 'host_os', 'version'] is not ['compiler', 'os', 'version']"
        >>> pr.add_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})
        Traceback (most recent call last):
            ...
        FileExistsError: such binary already exist
        >>> len(pr.list_package_binaries())
        1
        >>> pr.add_package_binary({'os':'linux', 'compiler':'gcc', 'version':'1.0'})
        >>> len(pr.list_package_binaries())
        2
        >>> pr.remove_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})
        >>> len(pr.list_package_binaries())
        1
        >>> pr.get_package_binary({'os':'linux', 'compiler':'gcc', 'version':'1.0'})
        PackageBinaryObject
        >>> pr.add_package_binary({'os':'linux', 'compiler':'g++', 'version':'1.0'})
        >>> pr.param_remove('compiler')
        Traceback (most recent call last):
        ...
        NameError: Cannot remove parameter compiler since it will cause two binary to have the same value
        >>> pr.param_add('stdlib', default_value='c++11')
        >>> pr
        PR[openssl, compiler, os, stdlib, version]
        >>> old_assignment = {'os':'linux', 'compiler':'g++', 'version':'1.0', 'stdlib': 'c++11'}
        >>> new_assignment = {'os':'linux', 'compiler':'g++', 'version':'1.0', 'stdlib': 'static_c++'}
        >>> pr.reassign_binary(old_assignment, new_assignment)
        >>> pr.param_remove('compiler')
        >>> pr
        PR[openssl, os, stdlib, version]
    """
    __params_prefix = '__params'

    def __init__(self, name: str, client: FileBasedClientAbstract, params: Optional[List[str]] = None):
        if not isinstance(client, FileBasedClientAbstract):
            raise TypeError("Must be using FileBasedClient")
        self.client = client
        super(PackageRegistryFileBased, self).__init__(name, params)

        remote_params = self.__get_remote_params()
        if params is None and remote_params is None:
            raise FileNotFoundError("you need to declare params if you are adding. if you are getting, this "
                                    "means that the package registry is not properly set, you need to delete and "
                                    "add again")
        elif remote_params is not None:  # ignore the passed params and use the remote one
            self.params = remote_params
        else:
            self.params = params
            self.client.mkdir(self.__serialize_params(self.params))

    def __repr__(self):
        return "PR[{}, {}]".format(self.name, ', '.join(sorted(self.params)))

    def __get_remote_params(self) -> Optional[List[str]]:
        params = None
        dirs = self.client.ls()
        for dir_name in dirs:
            if PackageRegistryFileBased.__params_prefix in dir_name:
                params = dir_name.split('==')[1:]
        return params

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

    def add_package_binary(self, assignment: Dict[str, str]) -> None:
        if set(assignment.keys()) != set(self.params):
            raise KeyError("wrong settings key: {} is not {}".format(sorted(assignment.keys()),
                                                                     sorted(self.params)))

        serialized_assignment = PackageRegistryFileBased.__serialize_assignment(assignment)
        mapping = self.__get_serialized_assignment_to_wrapper_mapping()
        if serialized_assignment in mapping:
            raise FileExistsError("such binary already exist")

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

    def get_package_binary(self, assignment: Dict[str, str]) -> PackageBinaryFileBased:
        serialized_assignment = PackageRegistryFileBased.__serialize_assignment(assignment)
        if set(assignment.keys()) != set(self.params):
            raise KeyError("wrong settings key: {} is not {}".format(sorted(assignment.keys()),
                                                                     sorted(self.params)))
        if serialized_assignment not in self.__get_serialized_assignment_to_wrapper_mapping():
            raise FileNotFoundError("such configuration does not exist")
        return PackageBinaryFileBased(
            self.client.dispatch_subdir(
                self.__get_serialized_assignment_to_wrapper_mapping()[serialized_assignment]
            ),
            registry_name=self.name,
            assignment=assignment,
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
