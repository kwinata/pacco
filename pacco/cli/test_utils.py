import io
import os
import shlex
from pathlib import Path

from pacco.cli.commands.pacco import Pacco
from pacco.cli.commands.utils.output_stream import OutputStream


class API:
    @staticmethod
    def __exec(command):
        stream = io.StringIO()
        stream_err = io.StringIO()
        Pacco('', OutputStream(stream=stream, stream_err=stream_err)).run(
            *(shlex.split(command)[1:])
        )
        if stream_err.getvalue():
            raise ChildProcessError(stream_err.getvalue())
        return stream.getvalue()

    @staticmethod
    def remote_list():
        return API.__exec("pacco remote list")

    @staticmethod
    def remote_add(remote):
        return API.__exec(
            "pacco remote add {} {} {}".format(remote['name'], remote['type'], ",".join(remote['args'])),
        )

    @staticmethod
    def remote_remove(remote):
        return API.__exec("pacco remote remove {}".format(remote['name']))

    @staticmethod
    def remote_list_default():
        return API.__exec("pacco remote list_default")

    @staticmethod
    def remote_set_default(remote_names):
        return API.__exec("pacco remote set_default" + "".join([" "+remote_name for remote_name in remote_names]))

    @staticmethod
    def registry_list(remote_name):
        return API.__exec("pacco registry list {}".format(remote_name))

    @staticmethod
    def registry_add(remote, registry, params):
        return API.__exec("pacco registry add {} {} {}".format(remote, registry, params))

    @staticmethod
    def registry_remove(remote, registry):
        return API.__exec("pacco registry remove {} {}".format(remote, registry))

    @staticmethod
    def registry_binaries(remote, registry):
        return API.__exec("pacco registry binaries {} {}".format(remote, registry))

    @staticmethod
    def registry_param_list(remote, registry):
        return API.__exec("pacco registry param_list {} {}".format(remote, registry))

    @staticmethod
    def registry_param_add(remote, registry, new_param, default_value):
        return API.__exec("pacco registry param_add {}".format(" ".join([remote, registry, new_param, default_value])))

    @staticmethod
    def registry_param_remove(remote, registry, obsolete_param):
        return API.__exec("pacco registry param_remove {}".format(" ".join([remote, registry, obsolete_param])))

    @staticmethod
    def binary_upload(remote, registry, path, assignment):
        return API.__exec("pacco binary upload {} {} {} {}".format(
            remote, registry, path, assignment
        ))

    @staticmethod
    def binary_download(remote, registry, path, assignment):
        return API.__exec("pacco binary download {} {} {} {}".format(
            remote, registry, path, assignment
        ))

    @staticmethod
    def binary_remove(remote, registry, assignment):
        return API.__exec("pacco binary remove {} {} {}".format(
            remote, registry, assignment
        ))

    @staticmethod
    def binary_reassign(remote, registry, old_assignment, new_assignment):
        return API.__exec("pacco binary reassign {} {} {} {}".format(
            remote, registry, old_assignment, new_assignment,
        ))

    @staticmethod
    def binary_get_location(registry, assignment):
        return API.__exec("pacco binary get_location {} {}".format(
            registry, assignment
        ))


class Settings:
    __home_path = str(Path.home())
    config_path = os.path.join(__home_path, ".pacco_config")
    local_pacco_path = os.path.join(__home_path, ".pacco")
    cache_path = os.path.join(__home_path, ".pacco_cache")

    __nexus_url = os.getenv('NEXUS_URL', None)
    # if not __nexus_url:
    #     raise EnvironmentError("Please set NEXUS_URL environment variable")
    __nexus_username = os.getenv('NEXUS_USERNAME', 'admin')
    __nexus_password = os.getenv('NEXUS_PASSWORD', 'admin123')  # default in nexus2

    remotes = [
        {
            'name': 'webdav',
            'type': 'webdav',
            'args': ['http://localhost/', 'pacco/', 'webdav', 'webdav'],

            # used by remote_factory
            'remote_type': 'webdav',
            'host_path': ('http://localhost/', 'pacco/'),
            'credential': ('webdav', 'webdav'),
        },
        {
            'name': 'local',
            'type': 'local',
            'args': ['default'],

            # used by remote_factory
            'remote_type': 'local',
            'path': '',
        },
        {
            'name': 'local-with-path',
            'type': 'local',
            'args': ['__test_path'],

            # used by remote_factory
            'remote_type': 'local',
            'path': '__test_path',
        },
        {
            'name': 'nexus-remote',
            'type': 'nexus_site',
            'args': [__nexus_url, __nexus_username, __nexus_password],

            # used by remote_factory
            'remote_type': 'nexus_site',
            'url': __nexus_url,
            'username': __nexus_username,
            'password': __nexus_password,
        },
        {
            'name': 'nexus-remote3',
            'type': 'nexus3',
            'args': ['http://localhost:8082', 'pacco', 'admin', 'admin123'],

            # used by remote_factory
            'remote_type': 'nexus3',
            'host_path': ('http://localhost:8082', '/'),
            'repository_name': 'pacco',
            'credential': ('admin', 'admin123'),
        },
    ]
