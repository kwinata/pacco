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

    def list_package_registries(self) -> List[Tuple[str, PackageRegistry]]:
        """
        List package registries in this package manager.

        Returns:
            The list of package registry name and package registry object tuples
        """
        raise NotImplementedError()

    def delete_package_registry(self, name: str) -> None:
        """
        Delete a package registry from the package manager.

        Args:
            name: the name of the package registry to be deleted.
        """
        raise NotImplementedError()

    def add_package_registry(self, name: str, settings_key: List[str]) -> PackageRegistry:
        """
        Add a new package registry to this package manager.

        Args:
            name: the name of the package. For printing purposes only.
            settings_key: the list of keys for the configuration parameter, e.g. ['os', 'compiler', 'version']
        Returns:
            The package registry object.
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
    def __init__(self, name: str, client: ClientAbstract, settings_key: Optional[List[str]] = None):
        self.name = name
        self.client = client
        self.settings_key = settings_key

    def list_package_binaries(self) -> List[Tuple[str, PackageBinary]]:
        """
        List the package binaries registered in this package registry

        Returns:
            list of tuples of the package binary name and object
        """
        raise NotImplementedError()

    def add_package_binary(self, settings_value: Dict[str, str]) -> Tuple[str, PackageBinary]:
        """
        Add a new package binary to this registry. Note that this will only declare the existance of the binary
        by creating a new directory, to upload the binary must be done through the ``PackageBinaryFileBased``
        object itself.

        Args:
            settings_value: the assignment of key value of the settings_key.
        Returns:
            The tuple of the name of the directory name (serialized version of the configuration) and the object
        Exceptions:
            KeyError: raised if the set of keys in the passed ``settings_value`` is different with ``settings_key``
            FileExistsError: raised if a package binary with the same configuration already exist.
        """
        raise NotImplementedError()

    def delete_package_binary(self, settings_value: Dict[str, str]):
        """
        Delete the package binary folder

        Args:
            settings_value: the configuration of the the package binary to be deleted
        """
        raise NotImplementedError()

    def get_package_binary(self, settings_value: Dict[str, str]) -> PackageBinary:
        """
        Get a reference to the ``PackageBinary`` object based on the settings value

        Args:
            settings_value: the configuration of the the package binary to get
        Returns:
            the object
        Exceptions:
            KeyError: when the key of the settings passed is not correct
            FileNotFoundError: when there is no binary with the configuration of settings value
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
