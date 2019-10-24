from pacco.manager.file_based.remote import LocalRemote, NexusSiteRemote


def instantiate_remote(name: str, serialized):
    if serialized['remote_type'] == 'local':
        return LocalRemote.create(name, serialized)
    elif serialized['remote_type'] == 'nexus_site':
        return NexusSiteRemote.create(name, serialized)
    else:
        raise ValueError("The remote_type {} is not supported, currently only supports [{}]".format(
            serialized['remote_type'], ", ".join(['local', 'nexus_site'])
        ))
