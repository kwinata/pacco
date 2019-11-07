from __future__ import annotations

import glob
import json
import logging
import os
import re
from typing import List, Tuple, Optional

import requests

from pacco.manager.file_based.utils.clients.abstract import FileBasedClientAbstract
from pacco.manager.file_based.utils.clients.helper import check_ascii


class Nexus3Client(FileBasedClientAbstract):
    def __init__(self, host_path: Tuple[str, str], repository_name: str, credential: Optional[Tuple[str, str]] = None,
                 clean=False):
        self.session = requests.session()
        self.session.stream = True

        self.__host = host_path[0]
        self.__repository_name = repository_name
        self.__api = self.__host + '/service/rest/v1/components/'
        self.__abspath = host_path[1]
        self.__abspath = self.__abspath.lstrip('/')
        self.session.cert = None
        if credential:
            self.session.auth = credential
        if clean:
            self.__clean()

    def __clean(self):
        for dir_name in self.__ls_dirs():
            self.rmdir(dir_name)

    @staticmethod
    def __validate_code(got: int, expected: List[int]):
        if got not in expected:
            raise ValueError(f'Unexpected HTTP code {got}, expected {expected}')

    def ls(self) -> List[str]:
        return [dir_name.rstrip('/') for dir_name in self.__ls_dirs()]

    def __ls_dirs(self) -> List[str]:
        items = self.__get_items()
        return [item['name'][len(self.__abspath):-len('.pacco')] for item in items if
                re.match(rf"{self.__abspath}[\w=]+/\.pacco", item['name'])]

    def __get_items(self):
        response = self.session.get(self.__api, params={'repository': self.__repository_name})
        Nexus3Client.__validate_code(response.status_code, [200])
        return json.loads(response.content)['items']

    def __get_id(self, name):
        nexus_file_name = self.__abspath+name
        items = self.__get_items()
        item_names_id = {item['name']: item['id'] for item in items}
        return item_names_id[nexus_file_name]

    def rmdir(self, name: str) -> None:
        name = name.rstrip('/') + '/'
        if name not in self.__ls_dirs():
            raise KeyError(f"Directory {name} is not found")
        items = self.__get_items()
        ids_to_remove = [item['id'] for item in items if item['name'].startswith(self.__abspath+name)]
        for id_to_remove in ids_to_remove:
            response = self.session.delete(f'{self.__api}{id_to_remove}')
            Nexus3Client.__validate_code(response.status_code, [204])

    def mkdir(self, name: str) -> None:
        name = name.rstrip('/') + '/'
        if name in self.__ls_dirs():
            raise KeyError(f"Directory {name} is already exists")
        self.__upload(b'', name+'.pacco')

    def dispatch_subdir(self, name: str) -> Nexus3Client:
        name = name.rstrip('/') + '/'
        return Nexus3Client(host_path=(self.__host, self.__abspath+name),
                            repository_name=self.__repository_name,
                            credential=self.session.auth)

    def download_dir(self, download_path: str) -> None:
        os.makedirs(download_path, exist_ok=True)
        items = self.__get_items()
        for item in items:
            if item['name'].startswith(self.__abspath) and not item['name'].endswith(".pacco"):
                response = self.session.get(f'{self.__host}/repository/{self.__repository_name}/{item["name"]}')
                self.__validate_code(response.status_code, [200])
                file_name = os.path.join(
                                download_path,
                                *item['name'][len(self.__abspath+'bin/'):].split('/')
                            )
                os.makedirs(os.path.join(*os.path.split(file_name)[:-1]), exist_ok=True)
                with open(file_name, "wb") as f:
                    f.write(response.content)

    def upload_dir(self, upload_path: str) -> None:
        if 'bin/' in self.ls():
            self.rmdir('bin/')

        prev_path = os.getcwd()
        os.chdir(upload_path)
        try:
            for file_name in glob.iglob('**/*', recursive=True):
                check_ascii(file_name)
                if os.path.isdir(file_name):
                    continue
                logging.info("Uploading file {}".format(file_name))
                with open(file_name, 'rb') as f:
                    self.__upload(f, 'bin/' + file_name)
        except Exception as e:
            raise e
        finally:
            os.chdir(prev_path)

    def __upload(self, byte_string, path):
        response = self.session.post(self.__api, params={'repository': self.__repository_name},
                                     data={'raw.directory': self.__abspath + os.path.join(*os.path.split(path)[:-1]),
                                           'raw.asset1.filename': os.path.split(path)[-1]},
                                     files={'raw.asset1': byte_string}, stream=True)
        Nexus3Client.__validate_code(response.status_code, [204])
