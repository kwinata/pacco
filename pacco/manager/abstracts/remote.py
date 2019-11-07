from typing import List, Dict

from pacco.manager.abstracts.package_registry import PackageRegistryAbstract
from pacco.manager.abstracts.registry_factory import create_registry_object


class RemoteAbstract:
    """
    Represent the existence of the manager in a remote. This class is the interface class with the
    expected behavior defined below.
    """

    def __init__(self, configuration: Dict[str, str]):
        self.configuration = configuration
        pass

    def __str__(self):
        return "[{}, {}]".format(self.configuration['name'], self.configuration['remote_type'])

    def add_package_registry(self, name: str, params: List[str]) -> None:
        """
        Add a new package registry to this package manager.

        Args:
            name: the name of the package. For printing purposes only.
            params: the list of keys for the configuration parameter, e.g. ['os', 'compiler', 'version']
        Exception:
            FileExistsError: raised if the package with the same name is found
        """
        dirs = self.list_package_registries()
        if name in dirs:
            raise FileExistsError("The package registry {} is already found".format(name))
        self.allocate_space(name)
        create_registry_object(name, params=params, context=self.get_registry_context(name))

    def get_package_registry(self, name: str) -> PackageRegistryAbstract:
        """
        Get a reference to the ``PackageRegistry`` object based on the settings value

        Args:
            name: the name of the package registry to get
        Returns:
            the object
        Exceptions:
            FileNotFoundError: when that package is not found or it is not set properly.
        """
        dirs = self.list_package_registries()
        if name not in dirs:
            raise FileNotFoundError("The package registry {} is not found".format(name))
        return create_registry_object(name, context=self.get_registry_context(name))

    def try_download(self, package_name: str, assignment: Dict[str, str], fresh_download: bool, dir_path: str) -> bool:
        if package_name in self.list_package_registries():
            pr: PackageRegistryAbstract = self.get_package_registry(package_name)
            if pr.try_download(assignment, fresh_download, dir_path):
                return True
        return False

    def __repr__(self):
        return "RemoteObject"

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

    def allocate_space(self, name: str):
        raise NotImplementedError()

    def get_registry_context(self, name: str):
        raise NotImplementedError()
