from setuptools import setup, find_packages

setup(
    name='pacco',
    version='0.2.7',
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
