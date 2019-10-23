from typing import List

from pacco.manager.interfaces.package_registry import PackageRegistryInterface


class PackageManagerInterface:
    """
    Represent the existence of the manager in a remote. This class is the interface class with the
    expected behavior defined below.
    """

    def __init__(self):
        pass

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

    def get_package_registry(self, name: str) -> PackageRegistryInterface:
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