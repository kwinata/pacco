**************
Pacco Tutorial
**************

Quick Start
===========

Installation
------------
Make sure that you are using python >= 3.7
Install the pacco from pip: ``pip install pacco`` and check the installation by ``pacco --version``

Let us download some file for example purposes::

    curl https://codeload.github.com/openssl/openssl/zip/OpenSSL_1_1_1d > openssl.zip
    unzip openssl.zip

In pacco, the hierarchy of "things" are remote->registry->binary. One remote simply means one directory in
the remote server. Registry mean one family of package (e.g., openssl, boost, etc.) and binary means one specific build
of the registry. Check the command by ``pacco -h``

Now let us set up a remote. For this tutorial, we will be using a locally hosted nexus2 docker server.
You can see the guide for installing the nexus from `here <https://github.com/sonatype/docker-nexus>`_.
After you run the server, add a hosted repository of provider ``site``. The url that we will use for this example is
``http://localhost:8081/nexus/content/sites/pacco-remote/``

Uploading
---------
If you run ``pacco remote -h`` you shall get something like::

  pacco remote add           Add a remote.
  pacco remote list          List existing remotes.
  pacco remote list_default  List default remote(s).
  pacco remote remove        Remove a remote.
  pacco remote set_default   Set default remote(s).

We will use ``pacco remote add`` to set up a remote. Use ``pacco remote add -h`` to see the arguments needed.
For now we will do ``pacco remote add docker-remote nexus_site``. It will ask you for further information needed.

After you successfully added the remote, check it with ``pacco remote list``.

Now, we shall add a registry to the remote. See how by checking ``pacco registry -h``. In this case, we can do
``pacco registry add docker-remote openssl version,type``. The ``version,type`` is a comma separated list (no space)
to indicate what is the parameters for the binaries. In this case, we actually storing a source code, so the version and
the openssl type (the "d") shall be enough.

Now check it with ``pacco registry list docker-remote``. Now we can upload the binary by
``pacco binary upload docker-remote openssl ./openssl version=1.1.1,type=d``

Now you shall be able to browse your nexus and see that the files is uploaded.

Using
-----

There is two way of using the binary that is already uploaded, one is to download directly to your project directory,
or get a pointer from pacco and use it from the pacco cache.

Download to project
^^^^^^^^^^^^^^^^^^^
``pacco binary download docker-remote openssl ./openssl-download version=1.1.1,type=d``

Use cache
^^^^^^^^^
When you download a new binary, pacco will actually store it into a cache and will not redownload if the parameter
configuration is the same. (you can force a fresh download by adding the flag ``--fresh-download``). Because you
might not want to have the whole copy for each of the project you are working on, pacco actually helps you to refer
to the binary cache location by using ``pacco binary get_location openssl version=1.1.1,type=d`` . And it will output
the directory of the installation
``/Users/kevin/.pacco_cache/__pacco_registry_name=openssl==type=d==version=1.1.1/bin``. To utilize this even better,
you shall not store the value directly in your project build script, but rather you can call the command online::

    export OPENSSL_DIR=$(pacco binary get_location openssl version=1.1.1,type=d)

Now you can use the variable ``OPENSSL_DIR`` in your build script as you need.


Next step
=========
.. toctree::
   :maxdepth: 1

   advanced_tutorial
