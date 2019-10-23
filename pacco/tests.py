import doctest

from pacco.manager import remote_manager
from pacco.manager.file_based import package_manager, package_registry, package_binary

doctest.testmod(package_manager)
doctest.testmod(package_registry)
doctest.testmod(package_binary)
doctest.testmod(remote_manager)
