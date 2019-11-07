from __future__ import annotations
import glob
import io
import logging
import os
import re
from typing import Optional, List

import requests
from bs4 import BeautifulSoup

from pacco.manager.file_based.utils.clients.abstract import FileBasedClientAbstract


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
        self.__session = requests.session()
        if username and password:
            self.__session.auth = (username, password)
        self.__dummy_stream = io.StringIO(".pacco")
        self.__connected = False
        self.__bin_dir = self.__url + 'bin/'

        self.__try_connect_nexus()
        if clean:
            self.__clean()

    def __clean(self) -> None:
        if not self.__connected:
            raise ConnectionError("Cannot clean if not connected")
        files_and_dirs = self.__ls_unformatted()
        for name in files_and_dirs:
            self.__rm(name)

    def __try_connect_nexus(self) -> None:
        resp = None
        if self.__session.get(self.__url + ".pacco").status_code == 200:
            self.__connected = True
            return
        try:
            resp = self.__session.post(self.__url + ".pacco", data=self.__dummy_stream)
        except requests.exceptions.ConnectionError:
            pass
        else:
            self.__connected = True
        finally:
            if not self.__connected or resp.status_code not in [200, 201, 204]:
                logging.warning("Connection to remote {} seems failed. "
                                "But you can still use Pacco's cache".format(self.__url))

    @staticmethod
    def __validate_status_code(received: int, expected: List[int]) -> None:
        if received not in expected:
            raise ValueError("Receiving http status {}, expecting one of {}".format(received, expected))

    def __ls_unformatted(self, path: Optional[str] = "") -> List[str]:
        if path and path[:-1] != "/":
            path += "/"
        resp = self.__session.get(self.__url + path)
        NexusFileClient.__validate_status_code(resp.status_code, [200])
        soup = BeautifulSoup(resp.content, 'html.parser')
        content = [str(tr.td.a.text) for tr in soup.find_all('tr')[2:]]  # skip table header and parent dir
        return content

    def ls(self) -> List[str]:
        return [dir_name[:-1] for dir_name in self.__ls_unformatted()]  # remove trailing space for dir name

    def rmdir(self, name: str) -> None:
        self.__rm(name+'/')

    def __rm(self, name: str) -> None:
        resp = self.__session.delete(self.__url + name)
        NexusFileClient.__validate_status_code(resp.status_code, [200, 204])

    def mkdir(self, name: str) -> None:
        resp = self.__session.post(self.__url+name+"/.pacco", data=self.__dummy_stream)
        NexusFileClient.__validate_status_code(resp.status_code, [200, 201])

    def dispatch_subdir(self, name: str) -> NexusFileClient:
        return NexusFileClient(self.__url+name+'/', self.__username, self.__password)

    def download_dir(self, download_path: str) -> None:
        self.dispatch_subdir('bin').__download_dir(download_path)

    def __download_dir(self, download_path: str) -> None:
        dirs_and_files = self.__ls_unformatted()
        os.makedirs(download_path, exist_ok=True)
        file_names = [name for name in dirs_and_files if name[-1] != '/']
        dir_names = [name for name in dirs_and_files if name[-1] == '/']
        for file_name in file_names:
            resp = self.__session.get(self.__url+file_name)
            NexusFileClient.__validate_status_code(resp.status_code, [200])
            logging.info("Downloading file {}".format(file_name))
            with open(os.path.join(download_path, file_name), 'wb') as f:
                f.write(resp.content)
        for dir_name in dir_names:
            child_object = NexusFileClient(self.__url+dir_name, self.__username, self.__password)
            child_object.download_dir(os.path.join(download_path, dir_name))

    def upload_dir(self, dir_path: str) -> None:
        if dir_path[:-1] != '/':
            dir_path += '/'

        self.__reset_bin_folder()

        prev_path = os.getcwd()
        os.chdir(dir_path)
        try:
            for file_name in glob.iglob('**/*', recursive=True):
                if os.path.isdir(file_name):
                    continue
                logging.info("Uploading file {}".format(file_name))
                with open(file_name, 'rb') as f:
                    resp = self.__session.post(self.__bin_dir + file_name, data=f)
                NexusFileClient.__validate_status_code(resp.status_code, [200, 201])
        except Exception as e:
            raise e
        finally:
            os.chdir(prev_path)

    def __reset_bin_folder(self) -> None:
        if 'bin' in self.__ls_unformatted():
            self.rmdir('bin')
        self.mkdir('bin')
