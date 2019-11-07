from typing import Dict

from pacco.manager.file_based.remote import RemoteFileBased
from pacco.manager.abstracts.remote import RemoteAbstract


def create_remote_object(configuration: Dict[str, str], clean=False) -> RemoteAbstract:
    if configuration['remote_type'] in ['local', 'nexus_site', 'webdav', 'nexus3']:
        return RemoteFileBased(configuration, clean)
    else:
        raise ValueError("The remote_type {} is not supported, currently only supports [{}]".format(
            configuration['remote_type'], ", ".join(['local', 'nexus_site'])
        ))
