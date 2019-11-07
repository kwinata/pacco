import os
import shutil

import pytest
import docker
from docker.errors import NotFound

from pacco.cli.test_utils import API, Settings
from pacco.manager.abstracts.remote_factory import create_remote_object


class PaccoTest:
    def setup_method(self, method):
        if os.path.exists(Settings.config_path):
            os.remove(Settings.config_path)
        if os.path.exists(Settings.local_pacco_path):
            shutil.rmtree(Settings.local_pacco_path)
        if os.path.exists(Settings.cache_path):
            shutil.rmtree(Settings.cache_path)
        client = docker.from_env()
        try:
            webdav_container = client.containers.get('webdav')
            webdav_container.start()
        except NotFound:
            print("Creating container")
            webdav_container = client.containers.create(
                "sashgorokhov/webdav:latest",
                name="webdav",
                ports={'80/tcp': 80},
                volumes={'/media': {'bind': '/media', 'mode': 'rw'}},
                environment={
                    'USERNAME': 'webdav',
                    'PASSWORD': 'webdav'
                },
                detach=True,
            )
            webdav_container.start()
        webdav_container.exec_run('rm -rf /media/pacco')
        webdav_container.exec_run('mkdir /media/pacco')
        webdav_container.exec_run('chmod o+rwxs /media/pacco')

    def teardown_method(self, method):
        self.setup_method(method)

    def format_list(self, items):
        return '[{}]\n'.format(", ".join(["'{}'".format(item) for item in items]))


@pytest.fixture(scope="function", params=Settings.remotes)
def remote(request):
    return request.param


class TestRemote(PaccoTest):
    def check_remote_list(self, remote_list):
        assert API.remote_list() == self.format_list(remote_list)

    def test_remote_add(self, remote):
        API.remote_add(remote)
        self.check_remote_list([remote['name']])

    def test_remote_remove(self, remote):
        API.remote_add(remote)
        API.remote_remove(remote)
        self.check_remote_list([])

    def check_remote_list_default(self, defaults):
        assert API.remote_list_default() == self.format_list(defaults)

    def test_remote_set_default(self, remote):
        API.remote_add(remote)
        API.remote_set_default([remote['name']])
        self.check_remote_list_default([remote['name']])
        API.remote_set_default([])
        self.check_remote_list_default([])


@pytest.fixture(scope="function")
def registry(remote):
    API.remote_add(remote)
    create_remote_object(remote, clean=True)
    yield "openssl"
    create_remote_object(remote, clean=True)
    API.remote_remove(remote)


class TestRegistry(PaccoTest):
    def check_registry_list(self, remote_name, registry_list):
        assert API.registry_list(remote_name) == self.format_list(registry_list)

    def test_registry_add(self, remote, registry):
        params = 'version,os,compiler'
        API.registry_add(remote['name'], registry, params)
        self.check_registry_list(remote['name'], [registry])
        API.registry_remove(remote['name'], registry)

    def test_registry_remove(self, remote, registry):
        params = 'version,os,compiler'
        API.registry_add(remote['name'], registry, params)
        API.registry_remove(remote['name'], registry)
        self.check_registry_list(remote['name'], [])

    def test_registry_param_list(self, remote, registry):
        params = 'version,os,compiler'
        API.registry_add(remote['name'], registry, params)
        print('lalas')
        assert API.registry_param_list(remote['name'], registry) == self.format_list(sorted(params.split(',')))

    @pytest.mark.parametrize("params,new_param",
                             [
                                 ('version,os,compiler', 'type'),
                                 pytest.param('arch,type', 'type', marks=pytest.mark.xfail),
                             ])
    def test_registry_param_add(self, remote, registry, params, new_param):
        default_value = 'debug'
        API.registry_add(remote['name'], registry, params)
        API.registry_param_add(remote['name'], registry, new_param, default_value)
        assert API.registry_param_list(remote['name'], registry) == \
            self.format_list(sorted(params.split(',') + [new_param]))

    @pytest.mark.parametrize("params,obsolete_param",
                             [
                                 ('version,os,compiler', 'os'),
                                 pytest.param('arch,type', 'os', marks=pytest.mark.xfail),
                             ])
    def test_registry_param_remove(self, remote, registry, params, obsolete_param):
        API.registry_add(remote['name'], registry, params)
        API.registry_param_remove(remote['name'], registry, obsolete_param)
        params = params.split(',')
        params.remove(obsolete_param)
        assert API.registry_param_list(remote['name'], registry) == self.format_list(sorted(params))


@pytest.fixture(scope="function")
def binary(remote, registry):
    API.registry_add(remote['name'], "openssl", "os,version")
    os.makedirs('openssl_upload_dir', exist_ok=True)
    os.makedirs('openssl_upload_dir/test', exist_ok=True)
    open("openssl_upload_dir/sample.a", "w").close()
    open("openssl_upload_dir/test/test.c", "w").close()
    params = 'os,version'.split(',')
    yield {
        'remote': remote['name'],
        'registry': 'openssl',
        'params': params,
        'path': 'openssl_upload_dir',
        'assignment_example': ",".join(["{}=test_value".format(param) for param in params]),
    }
    shutil.rmtree('openssl_upload_dir')


class TestBinary(PaccoTest):
    def check_binaries(self, remote_name, registry_name, expected_binaries):
        assert API.registry_binaries(remote_name, registry_name) == self.format_list(sorted(expected_binaries))

    @staticmethod
    def __upload_binary(binary):
        API.binary_upload(
            binary['remote'],
            binary['registry'],
            binary['path'],
            binary['assignment_example'],
        )

    def test_binary_upload(self, binary):
        TestBinary.__upload_binary(binary)
        self.check_binaries(binary['remote'], binary['registry'], [binary['assignment_example']])

    def test_binary_download(self, binary):
        TestBinary.__upload_binary(binary)
        if os.path.isdir('openssl_download_path'):
            shutil.rmtree('openssl_download_path')
        API.binary_download(
            binary['remote'],
            binary['registry'],
            'openssl_download_path',
            binary['assignment_example'],
        )
        assert os.path.isfile('openssl_download_path/sample.a')
        assert os.path.isfile('openssl_download_path/test/test.c')
        shutil.rmtree('openssl_download_path')

    def test_binary_remove(self, binary):
        TestBinary.__upload_binary(binary)
        API.binary_remove(
            binary['remote'],
            binary['registry'],
            binary['assignment_example'],
        )
        self.check_binaries(binary['remote'], binary['registry'], [])

    def test_binary_reassign(self, binary):
        old_assignment = binary['assignment_example']
        new_assignment = binary['assignment_example'].replace('test_value', 'new_value')
        TestBinary.__upload_binary(binary)
        API.binary_reassign(
            binary['remote'],
            binary['registry'],
            old_assignment,
            new_assignment,
        )
        self.check_binaries(
            binary['remote'],
            binary['registry'],
            [new_assignment]
        )

    def test_binary_get_location(self, binary):
        TestBinary.__upload_binary(binary)
        path = API.binary_get_location(
            binary['registry'],
            binary['assignment_example']
        )
        assert ".pacco_cache" in path
        shutil.rmtree(Settings.cache_path)
        API.remote_set_default([])
        try:
            API.binary_get_location(
                binary['registry'],
                binary['assignment_example']
            )
        except FileNotFoundError:
            pass
        else:
            assert False
        API.remote_set_default([binary['remote']])
        path = API.binary_get_location(
            binary['registry'],
            binary['assignment_example']
        )
        API.remote_set_default([])
        assert ".pacco_cache" in path
