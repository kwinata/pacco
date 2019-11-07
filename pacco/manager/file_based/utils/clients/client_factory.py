from pacco.manager.file_based.utils.clients.local import LocalClient
from pacco.manager.file_based.utils.clients.nexus import NexusFileClient
from pacco.manager.file_based.utils.clients.nexus3 import Nexus3Client
from pacco.manager.file_based.utils.clients.webdav import WebDavClient


def create_client_object(configuration, clean):
    if configuration['remote_type'] == 'local':
        if 'path' not in configuration:
            configuration['path'] = ''
        return LocalClient(path=configuration['path'], clean=clean)
    elif configuration['remote_type'] == 'nexus_site':
        return NexusFileClient(
            url=configuration['url'],
            username=configuration['username'],
            password=configuration['password'],
            clean=clean,
        )
    elif configuration['remote_type'] == 'webdav':
        return WebDavClient(
            host_path=configuration['host_path'],
            credential=configuration['credential'],
            clean=clean,
        )
    elif configuration['remote_type'] == 'nexus3':
        return Nexus3Client(
            host_path=configuration['host_path'],
            repository_name=configuration['repository_name'],
            credential=configuration['credential'],
            clean=clean,
        )
