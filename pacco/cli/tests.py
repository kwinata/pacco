import os
import shutil

import pytest

from pacco.cli.test_utils import API, Settings
from pacco.manager.remote_factory import instantiate_remote


class PaccoTest:
    def setup_method(self, method):
        if os.path.exists(Settings.config_path):
            os.remove(Settings.config_path)
        if os.path.exists(Settings.local_pacco_path):
            shutil.rmtree(Settings.local_pacco_path)

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
    instantiate_remote(remote['name'], remote, clean=True)
    yield "openssl"
    instantiate_remote(remote['name'], remote, clean=True)
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

    @pytest.mark.parametrize("params,assignment",
                             [('version,os,compiler', 'version=v1.2.3,os=ubuntu_16.04,compiler=g++'),
                              pytest.param('version,os,compiler', 'version=v1,compiler=g++', marks=pytest.mark.xfail),
                              pytest.param('version,os', 'version=v1,os=osx,compiler=g++', marks=pytest.mark.xfail),
                              ('version,os', 'os=ubuntu_16.04,version=v1.2.3'),
                              ('version,os', 'os=ubuntu_16.04,version=v1.2.3,'),
                              ])
    @pytest.mark.skip(reason="must wait for binary API")
    def test_registry_binaries(self, remote, registry, params, assignment):
        pass

    def test_registry_param_list(self, remote, registry):
        params = 'version,os,compiler'
        API.registry_add(remote['name'], registry, params)
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
