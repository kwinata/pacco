from pacco.manager.file_based.remote import LocalRemote, NexusSiteRemote


def instantiate_remote(name: str, serialized, clean=False):
    if serialized['remote_type'] == 'local':
        return LocalRemote.create(name, serialized, clean)
    elif serialized['remote_type'] == 'nexus_site':
        return NexusSiteRemote.create(name, serialized, clean)
    else:
        raise ValueError("The remote_type {} is not supported, currently only supports [{}]".format(
            serialized['remote_type'], ", ".join(['local', 'nexus_site'])
        ))
