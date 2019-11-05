import logging

from typing import Optional, Dict

from pacco.manager.file_based.utils.clients.abstract import FileBasedClientAbstract
from pacco.manager.abstracts.package_binary import PackageBinaryAbstract


class PackageBinaryFileBased(PackageBinaryAbstract):
    """
    An implementation of the PackageBinary interface
    """

    def __init__(self, client: FileBasedClientAbstract, registry_name: Optional[str] = None,
                 assignment: Optional[Dict[str, str]] = None):
        if not isinstance(client, FileBasedClientAbstract):
            raise TypeError("Must be using FileBasedClient")
        self.client = client
        super(PackageBinaryFileBased, self).__init__(registry_name, assignment)

    def fresh_download(self, download_dir_path: str) -> None:
        logging.info("fresh download")
        self.client.download_dir(download_dir_path)

    def upload_dir(self, dir_path: str) -> None:
        self.client.upload_dir(dir_path)
