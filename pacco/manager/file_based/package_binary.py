import logging

from typing import Optional, Dict

from pacco.manager.utils.cache import Cache
from pacco.manager.utils.clients import FileBasedClientAbstract
from pacco.manager.interfaces.package_binary import PackageBinaryInterface


class PackageBinaryFileBased(PackageBinaryInterface):
    """
    An implementation of the PackageBinary interface

    Examples:
        >>> from pacco.manager.utils.clients import LocalClient, NexusFileClient
        >>> client = LocalClient(clean=True)
        >>> import os
        >>> if 'NEXUS_URL' in os.environ: client = NexusFileClient(os.environ['NEXUS_URL'], 'admin', 'admin123', clean=True)
        >>> from pacco.manager.file_based.package_manager import PackageManagerFileBased
        >>> pm = PackageManagerFileBased(client)
        >>> pm.add_package_registry('openssl', ['os', 'compiler', 'version'])
        >>> pr = pm.get_package_registry('openssl')
        >>> pr.add_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})
        >>> pb = pr.get_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})
        >>> import os, shutil
        >>> os.makedirs('testfolder', exist_ok=True)
        >>> open('testfolder/testfile', 'w').close()
        >>> pb.upload_content('testfolder')
        >>> __ = shutil.move('testfolder/testfile', 'testfolder/testfile2')
        >>> pb_get = pr.get_package_binary({'os':'osx', 'compiler':'clang', 'version':'1.0'})  # use a new reference
        >>> pb_get.download_content('testfolder')
        >>> sorted(os.listdir('testfolder'))
        ['testfile', 'testfile2']
        >>> shutil.rmtree('testfolder')
    """

    def __init__(self, client: FileBasedClientAbstract, registry_name: Optional[str] = None,
                 assignment: Optional[Dict[str, str]] = None):
        if not isinstance(client, FileBasedClientAbstract):
            raise TypeError("Must be using FileBasedClient")
        self.client = client
        super(PackageBinaryFileBased, self).__init__()
        self.__registry_name = registry_name
        self.__cache = Cache()
        self.__assignment = assignment
        self.__cache_enabled = bool(self.__registry_name) and bool(self.__assignment)

    def __repr__(self):
        return "PackageBinaryObject"

    def download_content(self, download_dir_path: str, fresh_download: Optional[bool] = False) -> None:
        if self.__cache_enabled and (not fresh_download) and \
                self.__cache.download_from_cache(self.__registry_name, self.__assignment, download_dir_path):
            logging.info("use cache")
            return
        logging.info("fresh download")
        self.client.download_dir(download_dir_path)
        if self.__cache_enabled:
            logging.info("save cache")
            self.__cache.upload_to_cache(self.__registry_name, self.__assignment, download_dir_path)

    def upload_content(self, dir_path: str) -> None:
        self.client.upload_dir(dir_path)
        if self.__cache_enabled:
            self.__cache.upload_to_cache(self.__registry_name, self.__assignment, dir_path)