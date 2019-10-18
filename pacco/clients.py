from __future__ import annotations

import glob
import io
import os
import re
import shutil
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup


class ClientAbstract:
    pass


class FileBasedClientAbstract(ClientAbstract):
    """
    An interface for file-based client functionality.
    Each client shall have it's own context of current directory and it must not change throughout the lifetime.
    """
    def ls(self) -> List[str]:
        """
        List down the list of files and directories in it's directory

        Returns:
            list of files and directories as list of string
        """
        raise NotImplementedError()

    def rmdir(self, name: str) -> None:
        """
        Remove a directory recursively. The ``name`` directory must be inside
        this current directory.

        Args:
            name: the name of directory to be deleted
        """
        raise NotImplementedError()

    def mkdir(self, name: str) -> None:
        """
        Create a new directory under the current directory

        Args:
            name: The name of the directory ot be created
        """
        raise NotImplementedError()

    def dispatch_subdir(self, name: str) -> FileBasedClientAbstract:
        """
        Create and return new instance whose context is the join of this current directory with ``name``.

        Args:
            name: the directory name as namespace to the new client
        Return:
            the newly instantiated client
        """
        raise NotImplementedError()

    def download_dir(self, download_path: str) -> None:
        """
        Fetch the file content of this current directory (shall be used only by package binary), and put it
        into the ``download_path``.

        Args:
            download_path: the location destination of the downloaded directory
        """
        raise NotImplementedError()

    def upload_dir(self, dir_path: str) -> None:
        """
        Upload the ``dir_path`` to this current directory by first removing all the content then placing the uploaded
        file.

        Args:
            dir_path: the directory to be uploaded
        """
        raise NotImplementedError()


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
            self.rmdir(self.__root_dir)
            os.makedirs(self.__root_dir)

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
            if os.path.isdir(file_name):
                shutil.copytree(file_name, os.path.join(download_path, os.path.relpath(file_name, self.__bin_dir)))
            else:
                shutil.copy(file_name, os.path.join(download_path, os.path.relpath(file_name, self.__bin_dir)))

    def upload_dir(self, dir_path: str) -> None:
        shutil.rmtree(self.__bin_dir, ignore_errors=True)
        shutil.copytree(dir_path, self.__bin_dir)


class NexusFileClient(FileBasedClientAbstract):
    """
    An implementation of ``FileBasedClientAbstract``, using Nexus site repository as the file storage.
    """
    def __init__(self, url: str, username: str, password: str, clean: Optional[bool] = False) -> None:
        if not re.match(r'^https?://(\w+\.)*(\w+)(:\d+)?/(.+/)*$', url):
            raise ValueError("URL {} not valid, make sure you have trailing slash".format(url))
        self.__url = url
        self.__username = username
        self.__password = password
        self.__dummy_stream = io.StringIO(".pacco")

        resp = requests.post(url+".pacco", auth=(self.__username, self.__password), data=self.__dummy_stream)
        if resp.status_code not in [200, 201, 204]:
            raise ConnectionError("Connection seems failed, HTTP status code {}".format(resp.status_code))
        self.__bin_dir = url + 'bin/'

        if clean:
            files_and_dirs = self.__ls_unformatted()
            for name in files_and_dirs:
                self.__rm(name)

    @staticmethod
    def __validate_status_code(received: int, expected: List[int]) -> None:
        if received not in expected:
            raise ValueError("Receiving http status {}, expecting one of {}".format(received, expected))

    def __ls_unformatted(self) -> List[str]:
        resp = requests.get(self.__url, auth=(self.__username, self.__password))
        NexusFileClient.__validate_status_code(resp.status_code, [200])
        soup = BeautifulSoup(resp.content, 'html.parser')
        content = [str(tr.td.a.text) for tr in soup.find_all('tr')[2:]]  # skip table header and parent dir
        return content

    def ls(self) -> List[str]:
        return [dir_name[:-1] for dir_name in self.__ls_unformatted()]  # remove trailing space for dir name

    def rmdir(self, name: str) -> None:
        self.__rm(name+'/')

    def __rm(self, name: str) -> None:
        resp = requests.delete(self.__url + name, auth=(self.__username, self.__password))
        NexusFileClient.__validate_status_code(resp.status_code, [200, 204])

    def mkdir(self, name: str) -> None:
        resp = requests.post(self.__url+name+"/.pacco", auth=(self.__username, self.__password),
                             data=self.__dummy_stream)
        NexusFileClient.__validate_status_code(resp.status_code, [200, 201])

    def dispatch_subdir(self, name: str) -> NexusFileClient:
        return NexusFileClient(self.__url+name+'/', self.__username, self.__password)

    def download_dir(self, download_path: str) -> None:
        dirs_and_files = self.__ls_unformatted()
        os.makedirs(download_path, exist_ok=True)
        file_names = [name for name in dirs_and_files if name[-1] != '/']
        dir_names = [name for name in dirs_and_files if name[-1] == '/']
        for file_name in file_names:
            resp = requests.get(self.__url+file_name, auth=(self.__username, self.__password))
            NexusFileClient.__validate_status_code(resp.status_code, [200])
            with open(os.path.join(download_path, file_name), 'wb') as f:
                f.write(resp.content)
        for dir_name in dir_names:
            child_object = NexusFileClient(self.__url+dir_name, self.__username, self.__password)
            child_object.download_dir(os.path.join(download_path, dir_name))

    def upload_dir(self, dir_path: str) -> None:
        if dir_path[:-1] != '/':
            dir_path += '/'
        contents = self.__ls_unformatted()
        for content in contents:
            self.__rm(content)

        prev_path = os.getcwd()
        os.chdir(dir_path)
        try:
            for file_name in glob.iglob('**/*', recursive=True):
                if os.path.isdir(file_name):
                    continue
                with open(file_name, 'rb') as f:
                    resp = requests.post(self.__url + file_name, data=f, auth=(self.__username, self.__password))
                NexusFileClient.__validate_status_code(resp.status_code, [200, 201])
        except Exception as e:
            raise e
        finally:
            os.chdir(prev_path)
