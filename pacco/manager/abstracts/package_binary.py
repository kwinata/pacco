import logging
from typing import Optional, Dict

from pacco.manager.utils.cache import Cache


class PackageBinaryAbstract:
    """
        Represent the existence of a package (e.g. openssl) in the package manager
        This class is the interface class with the expected behavior defined below.
    """

    def __init__(self, registry_name: Optional[str] = None, assignment: Optional[Dict[str, str]] = None):
        self.registry_name = registry_name
        self.cache = Cache()
        self.assignment = assignment
        self.cache_enabled = bool(self.registry_name) and bool(self.assignment)

    def __repr__(self):
        return "PackageBinaryObject"

    def download_content(self, download_dir_path: str, fresh_download: Optional[bool] = False) -> None:
        """
        Download content of uploaded binary from the remote to the ``download_dir_path``

        Args:
            download_dir_path: the destination of download
            fresh_download: if true, will not use cache
        """
        if self.cache_enabled and (not fresh_download) and \
                self.cache.download_from_cache(self.registry_name, self.assignment, download_dir_path):
            logging.info("use cache")
            return
        self.fresh_download(download_dir_path)
        if self.cache_enabled:
            logging.info("save cache")
            self.cache.upload_to_cache(self.registry_name, self.assignment, download_dir_path)

    def upload_content(self, dir_path: str) -> None:
        """
        Remove the previous binary and upload the content of ``dir_path`` to the remote.

        Args:
            dir_path: the path to the directory to be uploaded
        """
        self.upload_dir(dir_path)
        if self.cache_enabled:
            self.cache.upload_to_cache(self.registry_name, self.assignment, dir_path)

    def fresh_download(self, download_dir_path: str) -> None:
        raise NotImplementedError()

    def upload_dir(self, dir_path: str) -> None:
        raise NotImplementedError()
