from __future__ import annotations

from typing import List, Tuple, Optional, Dict

from pacco.classes_interface import PackageManager, PackageRegistry, PackageBinary
from pacco.clients import FileBasedClientAbstract


class PackageManagerFileBased(PackageManager):
    """
    An implementation of the PackageManager interface

    Examples:
        >>> from pacco.clients import LocalClient
        >>> LocalClient().rmdir('')  # clean the .pacco directory
        >>> client = LocalClient()
        >>> pm = PackageManagerFileBased(client)
        >>> pm.list_package_registries()
        []
        >>> pm.add_package_registry('openssl', ['os', 'compiler', 'version'])
        PR[openssl, compiler, os, version]
        >>> pm.add_package_registry('boost', ['os', 'target', 'type'])
        PR[boost, os, target, type]
        >>> pm.add_package_registry('openssl', ['os', 'compiler', 'version'])
        Traceback (most recent call last):
            ...
        FileExistsError: The package registry openssl is already found
        >>> pm.list_package_registries()
        [('boost', PR[boost, os, target, type]), ('openssl', PR[openssl, compiler, os, version])]
        >>> pm.delete_package_registry('openssl')
        >>> pm.list_package_registries()
        [('boost', PR[boost, os, target, type])]
        >>> pm.get_package_registry('boost')
        PR[boost, os, target, type]
    """
    def __init__(self, client: FileBasedClientAbstract):
        if not isinstance(client, FileBasedClientAbstract):
            raise TypeError("Must be using FileBasedClient")
        super(PackageManagerFileBased, self).__init__(client)

    def list_package_registries(self) -> List[Tuple[str, PackageRegistryFileBased]]:
        dir_names = self.client.ls()
        return sorted([(dir_name, PackageRegistryFileBased(dir_name, self.client.dispatch_subdir(dir_name)))
                       for dir_name in dir_names], key=lambda x: x[0])

    def delete_package_registry(self, name: str) -> None:
        self.client.rmdir(name)

    def add_package_registry(self, name: str, settings_key: List[str]) -> PackageRegistryFileBased:
        dirs = self.client.ls()
        if name in dirs:
            raise FileExistsError("The package registry {} is already found".format(name))
        self.client.mkdir(name)
        return PackageRegistryFileBased(name, self.client.dispatch_subdir(name), settings_key)

    def get_package_registry(self, name: str) -> PackageRegistryFileBased:
        dirs = self.client.ls()
        if name not in dirs:
            raise FileNotFoundError("The package registry {} is not found".format(name))
        return PackageRegistryFileBased(name, self.client.dispatch_subdir(name))


class PackageRegistryFileBased(PackageRegistry):
    """
    An implementation of the PackageRegistry interface

    Examples:
        >>> from pacco.clients import LocalClient
        >>> LocalClient().rmdir('')  # clean the .pacco directory
        >>> client = LocalClient()
        >>> pm = PackageManagerFileBased(client)
        >>> pr = pm.add_package_registry('openssl', ['os', 'compiler', 'version'])
        >>> pr.list_package_binaries()
        []
        >>> pr.add_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})
        ('compiler=clang==os=osx==version=1.0', PackageBinaryObject)
        >>> pr.add_package_binary({'host_os':'osx', 'compiler':'clang', 'version':'1.0'})
        Traceback (most recent call last):
            ...
        KeyError: "wrong settings key: ['compiler', 'host_os', 'version'] is not ['compiler', 'os', 'version']"
        >>> pr.add_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})
        Traceback (most recent call last):
            ...
        FileExistsError: such binary already exist
        >>> pr.list_package_binaries()
        [('compiler=clang==os=osx==version=1.0', PackageBinaryObject)]
        >>> pr.add_package_binary({'os':'linux', 'compiler':'gcc', 'version':'1.0'})
        ('compiler=gcc==os=linux==version=1.0', PackageBinaryObject)
        >>> pr.list_package_binaries()
        [('compiler=clang==os=osx==version=1.0', PackageBinaryObject), \
('compiler=gcc==os=linux==version=1.0', PackageBinaryObject)]
        >>> pr.delete_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})
        >>> pr.list_package_binaries()
        [('compiler=gcc==os=linux==version=1.0', PackageBinaryObject)]
        >>> pr.get_package_binary({'os':'linux', 'compiler':'gcc', 'version':'1.0'})
        PackageBinaryObject
    """

    def __init__(self, name: str, client: FileBasedClientAbstract, settings_key: Optional[List[str]] = None):
        if not isinstance(client, FileBasedClientAbstract):
            raise TypeError("Must be using FileBasedClient")
        super(PackageRegistryFileBased, self).__init__(name, client, settings_key)
        from_remote = self.__get_settings_key()
        if settings_key is None and from_remote is None:
            raise FileNotFoundError("you need to declare settings_key if you are adding, if you are getting, this"
                                    "means that the package registry is not properly set, you need to delete and"
                                    "add again")
        elif from_remote is not None:  # ignore the passed settings_key and use the remote one
            self.settings_key = from_remote
        else:
            self.settings_key = settings_key
            self.client.mkdir(self.__generate_settings_key_dir_name(self.settings_key))

    def __repr__(self):
        return "PR[{}, {}]".format(self.name, ', '.join(sorted(self.settings_key)))

    def __get_settings_key(self) -> Optional[List[str]]:
        settings_key = None
        dirs = self.client.ls()
        for dir_name in dirs:
            if '__settings_key' in dir_name:
                settings_key = dir_name.split('==')[1:]
        return settings_key

    @staticmethod
    def __generate_settings_key_dir_name(settings_key: List[str]) -> str:
        settings_key = sorted(settings_key)
        return '=='.join(['__settings_key'] + settings_key)

    @staticmethod
    def __generate_dir_name_from_settings_value(settings_value: Dict[str, str]) -> str:
        sorted_settings_value_pair = sorted(settings_value.items(), key=lambda x: x[0])
        zipped_assignments = ['='.join(pair) for pair in sorted_settings_value_pair]
        return '=='.join(zipped_assignments)

    def list_package_binaries(self) -> List[Tuple[str, PackageBinaryFileBased]]:
        dirs = self.client.ls()
        dirs.remove(self.__generate_settings_key_dir_name(self.settings_key))
        return sorted([(name, PackageBinaryFileBased(self.client.dispatch_subdir(name))) for name in dirs],
                      key=lambda x: x[0])

    def add_package_binary(self, settings_value: Dict[str, str]) -> Tuple[str, PackageBinaryFileBased]:
        if set(settings_value.keys()) != set(self.settings_key):
            raise KeyError("wrong settings key: {} is not {}".format(sorted(settings_value.keys()),
                                                                     sorted(self.settings_key)))
        dir_name = PackageRegistryFileBased.__generate_dir_name_from_settings_value(settings_value)
        if dir_name in self.client.ls():
            raise FileExistsError("such binary already exist")
        self.client.mkdir(dir_name)
        return dir_name, PackageBinaryFileBased(self.client.dispatch_subdir(dir_name))

    def delete_package_binary(self, settings_value: Dict[str, str]):
        dir_name = PackageRegistryFileBased.__generate_dir_name_from_settings_value(settings_value)
        self.client.rmdir(dir_name)

    def get_package_binary(self, settings_value: Dict[str, str]) -> PackageBinaryFileBased:
        dir_name = PackageRegistryFileBased.__generate_dir_name_from_settings_value(settings_value)
        if set(settings_value.keys()) != set(self.settings_key):
            raise KeyError("wrong settings key: {} is not {}".format(sorted(settings_value.keys()),
                                                                     sorted(self.settings_key)))
        if dir_name not in self.client.ls():
            raise FileNotFoundError("such configuration does not exist")
        return PackageBinaryFileBased(self.client.dispatch_subdir(dir_name))


class PackageBinaryFileBased(PackageBinary):
    """
    An implementation of the PackageBinary interface

    Examples:
        >>> from pacco.clients import LocalClient
        >>> LocalClient().rmdir('')  # clean the .pacco directory
        >>> client = LocalClient()
        >>> pm = PackageManagerFileBased(client)
        >>> pr = pm.add_package_registry('openssl', ['os', 'compiler', 'version'])
        >>> name, pb = pr.add_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})
        >>> import os, shutil
        >>> os.makedirs('testfolder', exist_ok=True)
        >>> open('testfolder/testfile', 'w').close()
        >>> pb.upload_content('testfolder')
        >>> shutil.rmtree('testfolder')
        >>> os.listdir('testfolder')
        Traceback (most recent call last):
            ...
        FileNotFoundError: [Errno 2] No such file or directory: 'testfolder'
        >>> pb_get = pr.get_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})  # use a new reference
        >>> pb_get.download_content('testfolder')
        >>> os.listdir('testfolder')
        ['testfile']
        >>> shutil.rmtree('testfolder')
    """

    def __init__(self, client: FileBasedClientAbstract):
        if not isinstance(client, FileBasedClientAbstract):
            raise TypeError("Must be using FileBasedClient")
        super(PackageBinaryFileBased, self).__init__(client)

    def __repr__(self):
        return "PackageBinaryObject"

    def download_content(self, download_dir_path: str) -> None:
        self.client.download_dir(download_dir_path)

    def upload_content(self, dir_path: str) -> None:
        self.client.upload_dir(dir_path)
