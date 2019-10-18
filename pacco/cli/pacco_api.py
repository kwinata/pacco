from pacco.classes_file_based import PackageManagerFileBased
from pacco.clients import LocalClient
from pacco.cli.output_stream import OutputStream


class PaccoAPIV1:
    def __init__(self):
        self.__client = LocalClient()
        self.__pm = PackageManagerFileBased(self.__client)
        self.out = OutputStream()

    def download(self, registry: str, path: str, *settings: str):
        """
        Download binary, implemented using Pacco's predefined classes and methods.

        Args:
            registry: name of binary
            path: path to download binary
            settings: configuration of binary to be downloaded
        """

        def get_settings_dict(args):
            d = {}
            for s in args:
                if "=" not in s:
                    raise ValueError("settings must be in the form of <key>=<value>")
                key, value = s.split("=")
                d[key] = value
            return d

        try:
            pr = self.__pm.get_package_registry(registry)
            pb = pr.get_package_binary(get_settings_dict(settings))
            pb.download_content(path)
        except KeyError or ValueError as exc:
            self.out.writeln("{}".format(str(exc)), error=True)


PaccoAPI = PaccoAPIV1
