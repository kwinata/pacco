"""
Acknowledgement:
Implementation is sourced and inspired from https://github.com/amnong/easywebdav/
"""
from __future__ import annotations
import glob
import logging
import os
from typing import Optional, Tuple

import requests
from numbers import Number
import xml.etree.cElementTree as xmlTree


from http.client import responses as http_codes

from pacco.manager.file_based.utils.clients.abstract import FileBasedClientAbstract

DOWNLOAD_CHUNK_SIZE_BYTES = 1 * 1024 * 1024


class WebdavException(Exception):
    pass


class ConnectionFailed(WebdavException):
    pass


def translate_http_code(code: int) -> str:
    return http_codes.get(code, 'UNKNOWN')


def prop(elem, name, default=None):
    child = elem.find('.//{DAV:}' + name)
    return default if child is None else child.text


def elem_to_path(elem):
    return prop(elem, 'href')


class OperationFailed(WebdavException):
    _OPERATIONS = dict(
        HEAD="get header",
        GET="download",
        PUT="upload",
        DELETE="delete",
        MKCOL="create directory",
        PROPFIND="list directory",
    )

    def __init__(self, method, path, expected_code, actual_code):
        self.method = method
        self.path = path
        self.expected_code = expected_code
        self.actual_code = actual_code
        operation_name = self._OPERATIONS[method]
        self.reason = 'Failed to {operation_name} "{path}"'.format(**locals())
        expected_codes = (expected_code,) if isinstance(expected_code, Number) else expected_code
        expected_codes_str = ", ".join(
            '{0} {1}'.format(code, translate_http_code(code))
            for code in expected_codes
        )
        actual_code_str = translate_http_code(actual_code)
        msg = '''\
{self.reason}.
  Operation     :  {method} {path}
  Expected code :  {expected_codes_str}
  Actual code   :  {actual_code} {actual_code_str}'''.format(**locals())
        super(OperationFailed, self).__init__(msg)


class WebDavClient(FileBasedClientAbstract):
    def __init__(self, host_path: Tuple[str, str], credential: Optional[Tuple[str, str]] = None,
                 cert=None, clean=False):
        self.session = requests.session()
        self.session.stream = True

        self.__host = host_path[0]
        self.__abspath = host_path[1]
        self.url = "".join(host_path)
        self.session.cert = None
        if cert:
            self.session.cert = cert
            self.session.verify = True
        if credential:
            self.session.auth = credential
        if clean:
            self.__clean()

    def __clean(self):
        dir_names = self.ls()
        for dir_name in dir_names:
            self.rmdir(dir_name)

    def __send(self, method, path, expected_code, **kwargs):
        url = self.url+path
        response = self.session.request(method, url, allow_redirects=False, **kwargs)
        if isinstance(expected_code, Number) and response.status_code != expected_code \
                or not isinstance(expected_code, Number)\
                and response.status_code not in expected_code:
            raise OperationFailed(method, url, expected_code, response.status_code)
        return response

    def ls(self):
        headers = {'Depth': '1'}
        response = self.__send('PROPFIND', '', 207, headers=headers)
        tree = xmlTree.fromstring(response.content)
        elems = tree.findall('{DAV:}response')
        names = [elem_to_path(elem) for elem in elems]
        return self.__strip_leading_path(names)

    def __strip_leading_path(self, names):
        purged_result = []
        for name in names:
            if name.startswith('/' + self.__abspath):
                name = name[len(self.__abspath) + 1:].rstrip('/')
            if name:
                purged_result.append(name)
        return purged_result

    def mkdir(self, name):
        name = str(name).rstrip('/') + '/'
        self.__send('MKCOL', name, 201)

    def rmdir(self, name):
        name = str(name).rstrip('/') + '/'
        self.__send('DELETE', name, 204)

    def dispatch_subdir(self, name: str) -> WebDavClient:
        name = str(name).rstrip('/') + '/'
        return WebDavClient(
            host_path=(self.__host, self.__abspath+name),
            credential=self.session.auth,
            cert=self.session.cert
        )

    def download_dir(self, download_path):
        self.dispatch_subdir('bin').__download_dir(download_path)

    def __download_dir(self, download_path: str) -> None:
        dirs_and_files = self.ls()
        os.makedirs(download_path, exist_ok=True)
        for file_name in dirs_and_files:
            self.__download_file(file_name, os.path.join(download_path, file_name), (200, 301))

    def upload_dir(self, upload_path):
        if 'bin' in self.ls():
            self.__delete('bin')

        prev_path = os.getcwd()
        os.chdir(upload_path)
        try:
            for file_name in glob.iglob('**/*', recursive=True):
                if os.path.isdir(file_name):
                    continue
                logging.info("Uploading file {}".format(file_name))
                with open(file_name, 'rb') as f:
                    self.__upload(f, 'bin/' + file_name)
        except Exception as e:
            raise e
        finally:
            os.chdir(prev_path)

    def __delete(self, path):
        self.__send('DELETE', path, 204)

    def __upload(self, file_obj, remote_path):
        self.__send('PUT', remote_path, (200, 201, 204), data=file_obj)

    def __download_file(self, remote_path, local_path_or_file_obj, expected_code):
        response = self.__send('GET', remote_path, expected_code, stream=True)
        if isinstance(local_path_or_file_obj, str):
            with open(local_path_or_file_obj, 'wb') as f:
                WebDavClient.__write_download(f, response)
        else:
            WebDavClient.__write_download(local_path_or_file_obj, response)

    @staticmethod
    def __write_download(file_obj, response):
        for chunk in response.iter_content(DOWNLOAD_CHUNK_SIZE_BYTES):
            file_obj.write(chunk)
