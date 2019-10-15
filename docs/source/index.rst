*******************
Pacco Documentation
*******************

.. toctree::
   :maxdepth: 2

   api_docs/index
   diagram

Pacco is intended to be used a simple tool for storing binaries. Most of the existing tools found available
handles to much detail, usually because it is manifested as package manager for certain language.

Pacco knows three kinds of things: package manager, package registry, and package binary.
Package manager represent an existing of pacco managed "space". Package manager will store several package registries.
Each package registry represent a collection of binaries with different configuration. For example, we can have
a package registry of "openssl", which means it will store different variants or configurations of openssl.
The different variants or configuration is stored as package binaries. Technically, it does not need to be a program
binary, but rather any file. We store a directory inside the binary with the specified variant and configuration.

For more examples, you can see the API docs.
