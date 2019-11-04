from typing import Optional

from pacco.manager.interfaces.package_binary import PackageBinaryInterface


class PackageBinaryNexus3(PackageBinaryInterface):
    def __init__(self):
        pass

    def download_content(self, download_dir_path: str, fresh_download: Optional[bool] = False) -> None:
        raise NotImplementedError()

    def upload_content(self, dir_path: str) -> None:
        raise NotImplementedError()
