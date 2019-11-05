from __future__ import annotations
import glob
import logging
import os
import shutil
from pathlib import Path
from typing import Optional, List

from pacco.manager.file_based.utils.clients.abstract import FileBasedClientAbstract


class LocalClient(FileBasedClientAbstract):
    """
    An implementation of ``FileBasedClientAbstract``, using ``homepath/.pacco`` as the file storage.
    """
    def __init__(self, path: Optional[str] = "", clean: Optional[bool] = False) -> None:
        if path:
            self.__root_dir = path
            os.makedirs(self.__root_dir, exist_ok=True)
        else:
            self.__root_dir = os.path.join(str(Path.home()), '.pacco')
            os.makedirs(self.__root_dir, exist_ok=True)
        self.__bin_dir = os.path.join(self.__root_dir, 'bin')

        if clean:
            shutil.rmtree(self.__root_dir)
            os.makedirs(self.__root_dir)

        self.bin_dir_for_cache = self.__bin_dir

    def ls(self) -> List[str]:
        return os.listdir(self.__root_dir)

    def rmdir(self, name: str) -> None:
        shutil.rmtree(os.path.join(self.__root_dir, name))

    def mkdir(self, name: str) -> None:
        os.makedirs(os.path.join(self.__root_dir, name))

    def dispatch_subdir(self, name: str) -> LocalClient:
        return LocalClient(os.path.join(self.__root_dir, name))

    def download_dir(self, download_path: str) -> None:
        os.makedirs(download_path, exist_ok=True)
        for file_name in glob.iglob(os.path.join(self.__bin_dir, '*')):
            logging.info("Downloading file/folder {}".format(file_name))
            if os.path.isdir(file_name):
                shutil.copytree(file_name, os.path.join(download_path, os.path.relpath(file_name, self.__bin_dir)))
            else:
                shutil.copy(file_name, os.path.join(download_path, os.path.relpath(file_name, self.__bin_dir)))

    def upload_dir(self, dir_path: str) -> None:
        shutil.rmtree(self.__bin_dir, ignore_errors=True)
        shutil.copytree(dir_path, self.__bin_dir)
