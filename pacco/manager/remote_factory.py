from typing import Dict

from pacco.manager.file_based.package_manager import PackageManagerFileBased
from pacco.manager.interfaces.package_manager import PackageManagerInterface


def instantiate_remote(configuration: Dict[str, str], clean=False) -> PackageManagerInterface:
    if configuration['remote_type'] in ['local', 'nexus_site', 'webdav']:
        return PackageManagerFileBased(configuration, clean)
    else:
        raise ValueError("The remote_type {} is not supported, currently only supports [{}]".format(
            configuration['remote_type'], ", ".join(['local', 'nexus_site'])
        ))
