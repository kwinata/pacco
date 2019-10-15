# pacco
Pacco is a simple package manager (used for prebuilt binary) that is interoperable with Nexus repository manager.

## Publish to PyPI

To generate distribution archives, run `python3 setup.py sdist bdist_wheel`.

Use `python3 -m twine upload dist/*` to upload your package and enter your credentials for the account you have registered on the real PyPI.

Install from the real PyPI using `pip install pacco`.
