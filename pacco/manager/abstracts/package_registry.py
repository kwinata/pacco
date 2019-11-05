import copy
from typing import Optional, List, Dict, Callable

from pacco.manager.abstracts.binary_factory import create_binary_object
from pacco.manager.abstracts.package_binary import PackageBinaryAbstract


class PackageRegistryAbstract:
    """
    Represent the existence of a package (e.g. openssl) in the package manager.
    This class is the interface class with the expected behavior defined below.
    """

    def __init__(self, name: str, params: Optional[List[str]] = None):
        self.name = name
        self.params = params

        remote_params = self.get_remote_params()
        if params is None and remote_params is None:
            raise FileNotFoundError("you need to declare params if you are adding. if you are getting, this "
                                    "means that the package registry is not properly set, you need to delete and "
                                    "add again")
        elif remote_params is not None:  # ignore the passed params and use the remote one
            self.params = remote_params
        else:
            self.params = params
            self.initialize_remote_params(params)

    def __repr__(self):
        return "PR[{}, {}]".format(self.name, ', '.join(sorted(self.params)))

    def add_package_binary(self, assignment: Dict[str, str]) -> None:
        """
        Add a new package binary to this registry. Note that this will only declare the existence of the binary
        by creating a new directory, to upload the binary must be done through the ``PackageBinaryFileBased``
        object itself.

        Args:
            assignment: the assignment of key value of the params.
        Exceptions:
            KeyError: raised if the set of keys in the passed ``assignment`` is different with ``params``
            FileExistsError: raised if a package binary with the same configuration already exist.
        """
        if set(assignment.keys()) != set(self.params):
            raise KeyError("wrong settings key: {} is not {}".format(sorted(assignment.keys()),
                                                                     sorted(self.params)))
        if PackageRegistryAbstract.check_assignment_in(assignment, self.list_package_binaries()):
            raise FileExistsError("such binary already exist")
        self.allocate_space_for_binary(assignment)

    def get_package_binary(self, assignment: Dict[str, str]) -> PackageBinaryAbstract:
        """
        Get a reference to the ``PackageBinary`` object based on the settings value

        Args:
            assignment: the configuration of the the package binary to get
        Returns:
            the object
        Exceptions:
            KeyError: when the key of the settings passed is not correct
            FileNotFoundError: when there is no binary with the configuration of settings value
        """
        if set(assignment.keys()) != set(self.params):
            raise KeyError("wrong settings key: {} is not {}".format(sorted(assignment.keys()),
                                                                     sorted(self.params)))
        if PackageRegistryAbstract.check_assignment_in(assignment, self.list_package_binaries()):
            return create_binary_object(registry_name=self.name,
                                        assignment=assignment,
                                        context=self.get_binary_context(assignment))
        raise FileNotFoundError("such configuration does not exist")

    def param_list(self) -> List[str]:
        """
        List the declared parameters of the ```PackageRegistry```
        """
        return self.params

    def param_add(self, name: str, default_value: Optional[str] = "default") -> None:
        """
        Append new parameter to each ``PackageBinary`` object and assign ``default_value`` as
        the default value to the new parameter

        Args:
            name: the new param name
            default_value: the default value to be assigned
        Exceptions:
            ValueError: if the param is already exist
        """
        if name in self.params:
            raise ValueError("{} already in params".format(name))
        old_params = copy.deepcopy(self.params)
        self.params.append(name)
        self.reset_remote_params(old_params, self.params)
        self.rename_serialized_assignment(lambda x: x.update({name: default_value}))

    def rename_serialized_assignment(self, action: Callable[[Dict[str, str]], None]):
        for assignment in self.list_package_binaries():
            new_assignment = copy.deepcopy(assignment)
            action(new_assignment)
            self.reset_binary_assignment(assignment, new_assignment)

    def param_remove(self, name: str) -> None:
        """
        Remove a parameter from each ``PackageBinary`` object

        Args:
            name: the param name to be deleted
        Exceptions:
            ValueError: if the param name does not exist
            NameError: if the resulting assignments will have duplicate when the param is removed
        """
        if name not in self.params:
            raise ValueError("{} not in params".format(name))
        new_set_of_assignment = set()
        for assignment in self.list_package_binaries():
            del assignment[name]
            if PackageRegistryAbstract.check_assignment_in(assignment, list(new_set_of_assignment)):
                raise NameError("Cannot remove parameter {} since it will cause "
                                "two binary to have the same value".format(name))
            new_set_of_assignment.add(assignment)
        old_params = copy.deepcopy(self.params)
        self.params.remove(name)
        self.reset_remote_params(old_params, self.params)
        self.rename_serialized_assignment(lambda x: x.pop(name))

    @staticmethod
    def check_assignment_in(assignment: Dict[str, str], assignments: List[Dict[str, str]]):
        for other_assignment in assignments:
            if not (other_assignment.items() ^ assignment.items()):
                return True
        return False

    def reassign_binary(self, old_assignment: Dict[str, str], new_assignment: Dict[str, str]) -> None:
        """
        Reassign a new assignment to an existing binary

        Args:
            old_assignment: the old assignment
            new_assignment: the new assignment
        Exceptions:
            KeyError: if the key in the new assignment does not match with params
            ValueError: if there is no binary that match old_assignment
            NameError: there already exist binary with the same configuration as new_assignment
        """
        if set(new_assignment.keys()) != set(self.params):
            raise KeyError("wrong settings key: {} is not {}".format(sorted(new_assignment.keys()),
                                                                     sorted(self.params)))
        if not PackageRegistryAbstract.check_assignment_in(old_assignment, self.list_package_binaries()):
            raise ValueError("there is no binary that match the assignment")
        if PackageRegistryAbstract.check_assignment_in(new_assignment, self.list_package_binaries()):
            raise NameError("there already exist binary with same assignment with the new one")

        self.reset_binary_assignment(old_assignment, new_assignment)

    def try_download(self, assignment: Dict[str, str], fresh_download: bool, dir_path: str) -> bool:
        if assignment in self.list_package_binaries():
            pb: PackageBinaryAbstract = self.get_package_binary(assignment)
            pb.download_content(download_dir_path=dir_path, fresh_download=fresh_download)
            return True
        return False

    def get_remote_params(self) -> Optional[List[str]]:
        raise NotImplementedError()

    def initialize_remote_params(self, params: List[str]):
        raise NotImplementedError()

    def reset_remote_params(self, old_params: List[str], new_params: List[str]):
        raise NotImplementedError()

    def list_package_binaries(self) -> List[Dict[str, str]]:
        """
        List the package binaries registered in this package registry

        Returns:
            list of the package binary assignment dictionaries
        """
        raise NotImplementedError()

    def reset_binary_assignment(self, assignment: Dict[str, str], new_assignment: Dict[str, str]):
        raise NotImplementedError()

    def get_binary_context(self, assignment: Dict[str, str]):
        raise NotImplementedError()

    def allocate_space_for_binary(self, assignment: Dict[str, str]) -> None:
        raise NotImplementedError()

    def remove_package_binary(self, assignment: Dict[str, str]):
        """
        Delete the package binary folder

        Args:
            assignment: the configuration of the the package binary to be deleted
        """
        raise NotImplementedError()
