import os
import re
from setuptools import setup, find_packages


def load_version():
    """Loads a file content"""
    filename = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            "pacco", "__init__.py"))
    with open(filename, "rt") as version_file:
        pacco_init = version_file.read()
        version = re.search("__version__ = \"([0-9a-z.-]+)\"", pacco_init).group(1)
        return version


setup(
    name='pacco',
    version=load_version(),
    packages=find_packages(),
    author="Kevin Winata",
    author_email="kevinwinatamichael@gmail.com",
    description="A simple package manager (used for prebuilt binary), interoperable with Nexus repository manager",
    url="https://kwinata.github.io/pacco/",
    entry_points={
        'console_scripts': [
            'pacco=pacco.cli.entry_point:run'
        ]
    },
    install_requires=[
        'requests',
        'beautifulsoup4',
        'PyYAML',
    ],
    python_requires='>=3.7',
)
