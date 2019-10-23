from typing import Optional, List, Dict

from pacco.manager.interfaces.package_binary import PackageBinaryInterface


class PackageRegistryInterface:
    """
    Represent the existence of a package (e.g. openssl) in the package manager.
    This class is the interface class with the expected behavior defined below.
    """

    def __init__(self, name: str, params: Optional[List[str]] = None):
        self.name = name
        self.params = params

    def list_package_binaries(self) -> List[Dict[str, str]]:
        """
        List the package binaries registered in this package registry

        Returns:
            list of the package binary assignment dictionaries
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    def remove_package_binary(self, assignment: Dict[str, str]):
        """
        Delete the package binary folder

        Args:
            assignment: the configuration of the the package binary to be deleted
        """
        raise NotImplementedError()

    def get_package_binary(self, assignment: Dict[str, str]) -> PackageBinaryInterface:
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
        raise NotImplementedError()

    def param_list(self) -> List[str]:
        """
        List the declared parameters of the ```PackageRegistry```
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    def param_remove(self, name: str) -> None:
        """
        Remove a parameter from each ``PackageBinary`` object

        Args:
            name: the param name to be deleted
        Exceptions:
            ValueError: if the param name does not exist
            NameError: if the resulting assignments will have duplicate when the param is removed
        """
        raise NotImplementedError()

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
        raise NotImplementedError()
