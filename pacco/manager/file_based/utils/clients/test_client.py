import os

import pytest

from pacco.manager.file_based.utils.clients.local import LocalClient
from pacco.manager.file_based.utils.clients.nexus import NexusFileClient
from pacco.manager.file_based.utils.clients.nexus3 import Nexus3Client
from pacco.manager.file_based.utils.clients.webdav import WebDavClient


clients = [
    # (LocalClient, []),
    # (NexusFileClient, ['http://localhost:8081/nexus/content/sites/pacco/', 'admin', 'admin123']),
    # (WebDavClient, [('http://localhost/', 'pacco/'), ('webdav', 'webdav')]),
    (Nexus3Client, [('http://localhost:8082', '/'), 'pacco', ('admin', 'admin123')])
]


@pytest.fixture(scope="module", params=clients)
def client_class(request):
    return request.param


@pytest.fixture(scope="function")
def client(client_class):
    client_obj = client_class[0](*client_class[1], clean=True)
    yield client_obj
    client_class[0](*client_class[1], clean=True)


class TestClient:
    def test_ls(self, client):
        assert [] == client.ls()

    def test_mkdir_rmdir(self, client):
        client.mkdir('abc')
        assert ['abc'] == client.ls()
        client.rmdir('abc')
        assert [] == client.ls()

    def test_upload_download_dir(self, client):
        os.makedirs("test_dir", exist_ok=True)
        open("test_dir/text.txt", "w").close()
        client.upload_dir("test_dir")
        os.remove('test_dir/text.txt')
        os.rmdir('test_dir')

        client.download_dir('test_dir')
        assert os.path.isdir('test_dir')
        assert os.path.isfile('test_dir/text.txt')
        os.remove('test_dir/text.txt')
        os.rmdir('test_dir')
