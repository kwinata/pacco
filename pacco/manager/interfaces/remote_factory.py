from typing import Dict

from pacco.manager.file_based.remote import RemoteFileBased
from pacco.manager.interfaces.remote import RemoteInterface


def create_remote_object(configuration: Dict[str, str], clean=False) -> RemoteInterface:
    if configuration['remote_type'] in ['local', 'nexus_site', 'webdav']:
        return RemoteFileBased(configuration, clean)
    else:
        raise ValueError("The remote_type {} is not supported, currently only supports [{}]".format(
            configuration['remote_type'], ", ".join(['local', 'nexus_site'])
        ))