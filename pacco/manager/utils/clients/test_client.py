import os

import pytest

from pacco.manager.utils.clients.local import LocalClient
from pacco.manager.utils.clients.nexus import NexusFileClient
from pacco.manager.utils.clients.webdav import WebDavClient

clients = [
    LocalClient(clean=True),
    # NexusFileClient('http://localhost:8081/nexus/content/sites/pacco/', 'admin', 'admin123', clean=True),
    WebDavClient('http://localhost/', 'pacco/', 'webdav', 'webdav', clean=True),
]
@pytest.fixture(scope="function", params=clients)
def client(request):
    return request.param


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
