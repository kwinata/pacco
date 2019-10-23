from typing import Optional


class PackageBinaryInterface:
    """
        Represent the existence of a package (e.g. openssl) in the package manager
        This class is the interface class with the expected behavior defined below.
    """

    def __init__(self):
        pass

    def download_content(self, download_dir_path: str, fresh_download: Optional[bool] = False) -> None:
        """
        Download content of uploaded binary from the remote to the ``download_dir_path``

        Args:
            download_dir_path: the destination of download
            fresh_download: if true, will not use cache
        """
        raise NotImplementedError()

    def upload_content(self, dir_path: str) -> None:
        """
        Remove the previous binary and upload the content of ``dir_path`` to the remote.

        Args:
            dir_path: the path to the directory to be uploaded
        """
        raise NotImplementedError()
