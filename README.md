[![Build Status](https://travis-ci.org/kwinata/pacco.svg?branch=master)](https://travis-ci.org/kwinata/pacco)
[![PyPi version](https://pypip.in/v/pacco/badge.png)](https://pypi.org/project/pacco/)

# Pacco
![](docs/source/_images/pacco.png)

Pacco is a simple package manager (used for prebuilt binary) that is interoperable with Nexus repository manager.

## Usage

To download a registry, run `pacco download <registry> <path> <settings_key=settings_value> (<settings_key=settings_value> ...)`.

## Install
```
pip install pacco
```

## CLI Test

You need to have [bats](https://github.com/sstephenson/bats) installed in order to run tests for CLI.
```
bats tests/cli.bats
```