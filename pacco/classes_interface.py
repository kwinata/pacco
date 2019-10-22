from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from pacco.clients import ClientAbstract


class PackageManager:
    """
    Represent the existence of the manager in a remote. This class is the interface class with the
    expected behavior defined below.
    """
    def __init__(self, client: ClientAbstract):
        self.client = client

    def list_package_registries(self) -> List[str]:
        """
        List package registries in this package manager.

        Returns:
            The list of package registry name
        """
        raise NotImplementedError()

    def remove_package_registry(self, name: str) -> None:
        """
        Delete a package registry from the package manager.

        Args:
            name: the name of the package registry to be deleted.
        """
        raise NotImplementedError()

    def add_package_registry(self, name: str, params: List[str]) -> None:
        """
        Add a new package registry to this package manager.

        Args:
            name: the name of the package. For printing purposes only.
            params: the list of keys for the configuration parameter, e.g. ['os', 'compiler', 'version']
        Exception:
            FileExistsError: raised if the package with the same name is found
        """
        raise NotImplementedError()

    def get_package_registry(self, name: str) -> PackageRegistry:
        """
        Get a reference to the ``PackageRegistry`` object based on the settings value

        Args:
            name: the name of the package registry to get
        Returns:
            the object
        Exceptions:
            FileNotFoundError: when that package is not found or it is not set properly.
        """
        raise NotImplementedError()


class PackageRegistry:
    """
    Represent the existence of a package (e.g. openssl) in the package manager.
    This class is the interface class with the expected behavior defined below.
    """
    def __init__(self, name: str, client: ClientAbstract, params: Optional[List[str]] = None):
        self.name = name
        self.client = client
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
        Add a new package binary to this registry. Note that this will only declare the existance of the binary
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

    def get_package_binary(self, assignment: Dict[str, str]) -> PackageBinary:
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

    def append_param(self, name: str, default_value: Optional[str] = "default") -> None:
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

    def delete_param(self, name: str) -> None:
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


class PackageBinary:
    """
        Represent the existence of a package (e.g. openssl) in the package manager
        This class is the interface class with the expected behavior defined below.
    """
    def __init__(self, client: ClientAbstract):
        self.client = client

    def download_content(self, download_dir_path: str) -> None:
        """
        Download content of uploaded binary from the remote to the ``download_dir_path``

        Args:
            download_dir_path: the destination of download
        """
        raise NotImplementedError()

    def upload_content(self, dir_path: str) -> None:
        """
        Remove the previous binary and upload the content of ``dir_path`` to the remote.

        Args:
            dir_path: the path to the directory to be uploaded
        """
        raise NotImplementedError()
