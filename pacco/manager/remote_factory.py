from pacco.manager.file_based.package_manager import PackageManagerFileBased


def instantiate_remote(configuration, clean=False):
    if configuration['remote_type'] in ['local', 'nexus_site', 'webdav']:
        return PackageManagerFileBased(configuration, clean)
    else:
        raise ValueError("The remote_type {} is not supported, currently only supports [{}]".format(
            configuration['remote_type'], ", ".join(['local', 'nexus_site'])
        ))
