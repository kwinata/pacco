Quick Start
===========

Installation
------------
Make sure that you are using python >= 3.7
Install the pacco from pip: ``pip install pacco`` (or alternatively ``python -m pip install pacco`` and check the
installation by ``pacco --version``

Prepare file example
--------------------
Let us download some file for example purposes::

    $ curl https://codeload.github.com/openssl/openssl/zip/OpenSSL_1_1_1d > openssl.zip
    $ unzip openssl.zip
    $ rm openssl
    $ mv openssl-OpenSSL_1_1_1d openssl


Setup the remote server
-----------------------
For this tutorial, we will be using a locally hosted nexus2 docker server.
You can see the guide for setting up the dockerized nexus from `here <https://github.com/sonatype/docker-nexus>`_.
After you run the server, add a hosted repository of provider ``site``. The url that we will use for this example is
``http://localhost:8081/nexus/content/sites/my-pacco-repo/``.

If you feel that there is no need to or complicated to use the nexus server, you can opt to use the local server and
you can still follow along this tutorial.

Add the remote server to Pacco
------------------------------
After you have set up the repository on the Nexus, now we can add it to the Pacco. Since we are setting up a remote,
we can check what command do we need by using::

  $ pacco remote -h

          pacco remote add           Add a remote.
          pacco remote list          List existing remotes.
          pacco remote list_default  List default remote(s).
          pacco remote remove        Remove a remote.
          pacco remote set_default   Set default remote(s).

      Pacco remote commands. Type 'pacco remote <command> -h' for help

So clearly we need to add it first, you can see how to do it by::

    $ pacco remote add -h

    usage: pacco remote add [-h] name type args

    positional arguments:
      name        remote name
      type        remote type, choices: 'local', 'nexus_site', 'webdav', 'nexus3'
      args        remote args, a comma separated value(s) (with no space)
                  depending on the remote type. (1) For local, it's the path (can
                  be empty). (2) For nexus_site, it's the url, username, and
                  password. (3) For webdav, it's the host url, directory path,
                  username, and password (4) For nexus3, it's the host url,
                  repository name, username and password

    optional arguments:
      -h, --help  show this help message and exit


For now we will do::

    $ pacco remote add docker-remote nexus_site http://localhost:8081/nexus/content/sites/my-pacco-repo/,admin,admin123

.. note::   If you do not need authentication or you just want to read from the server (no write), you might not need
            the username and password (or even you might not have one). In this case, you can just put the username and password
            empty, such that the ``args`` will become ``http://localhost:8081/nexus/content/sites/my-pacco-repo/,,``.
            (note that you still need to put the ``,,``)

.. note::   If you use local remote instead, you can just do ``pacco remote add {REMOTE_NAME} local``.

After you successfully added the remote, check it with::

    $ pacco remote list

    ['docker-remote']

Setup a registry
----------------

Now, we shall add a registry to the remote. See how by checking::

    $ pacco registry -h

      pacco registry add           Add registry to remote.
      pacco registry binaries      List binaries of a registry from a specific remote.
      pacco registry list          List registries of a remote.
      pacco registry param_add     Add new parameter with default value to the binaries.
      pacco registry param_list    List params of a registry.
      pacco registry param_remove  Remove an existing parameter from all binaries.
      pacco registry remove        Remove a registry from a specific remote.

    Pacco registry commands. Type 'pacco registry <command> -h' for help


Because we downloaded openssl in the :ref:`Prepare file example`, we will name our registry to be just ``openssl``.

Let us check the arguments needed to add the registry::

    $ pacco remote add -h

    usage: pacco registry add [-h] remote name settings

    positional arguments:
      remote      remote name
      name        registry name
      settings    settings key (e.g. os,version,obfuscation)

    optional arguments:
      -h, --help  show this help message and exit

Notice that we need to provide the argument settings. This settings is like the "parameter names" that we will use
between the binaries associated with the registry. Since we are downloaded the openssl source (not binary), the
settings keys "version" and "type" seems reasonable. ::

    $ pacco registry add docker-remote openssl version,type

Now let's check it::

    $ pacco registry list docker-remote

    ['openssl']

You can also check the parameter list set::

    $ pacco registry param_list docker-remote openssl

    ['type', 'openssl']

Upload binary
-----------------
Now we can upload the "binary" (though it's actually a source code in our case). To see how we can do that ::

    $ pacco binary -h

      pacco binary download      Download from a specified or default remote. Will use cache if exists unless enforced by '--fresh-download' flag
      pacco binary get_location  Get the path to the cache location for the binary.
      pacco binary reassign      Change the assignment of a binary to a new one
      pacco binary remove        Remove a binary from a remote
      pacco binary upload        Upload binary to a specified remote and store it to cache.

    Pacco binary commands. Type 'pacco binary <command> -h' for help

    usage: pacco binary download [-h] remote_name registry_name dir_path settings

    $ pacco binary download -h

    positional arguments:
      remote_name    remote name
      registry_name  registry name
      dir_path       download path
      settings       settings for the specified registry (e.g.
                     os=linux,version=2.1.0,type=debug

    optional arguments:
      -h, --help     show this help message and exit


We need to make sure that the openssl directory is already in our working directory (or else you must provide the
absolute path). Then we can upload it to the server ::

    $ ls

    openssl

    $ ls openssl

    ACKNOWLEDGEMENTS Configurations   LICENSE          NOTES.PERL       README           apps             config.com       e_os.h           include          test
    AUTHORS          Configure        NEWS             NOTES.UNIX       README.ENGINE    appveyor.yml     crypto           engines          ms               tools
    CHANGES          FAQ              NOTES.ANDROID    NOTES.VMS        README.FIPS      build.info       demos            external         os-dep           util
    CONTRIBUTING     INSTALL          NOTES.DJGPP      NOTES.WIN        VMS              config           doc              fuzz             ssl

    $ pacco binary upload docker-remote openssl openssl version=1.1.1,type=d

Now we can confirm that it is uploaded::

    $ pacco registry binaries docker-remote openssl

    ['type=d,version=1.1.1']

Though not recommended, you may also browse through your nexus server and you can see that it is uploaded.

.. figure:: assets/screenshotNexus.png
    :figclass: align-center

Using the binary
----------------
There is two way of using the binary that is already uploaded, one is to download directly to your project directory,
or get a pointer from pacco and use it from the pacco cache.

Download to project directory
-----------------------------
The way you upload and download is similar, you need to specify the destination of the download and also the parameter
settings. If the a binary with the same registry and same parameter assignment (regardless of the remote source) was
downloaded previously, Pacco will just copy it from the cache (Pacco will automatically store to the cache for any
download or upload action).
You can enforce the download by adding the flag
``--fresh-download``. ::

    $ # remove pacco's cache
    $ rm -rf ~/.pacco
    $
    $ # download from server because the cache is empty
    $ pacco binary download docker-remote openssl ./openssl-download version=1.1.1,type=d
    $
    $ # will use the cache
    $ pacco binary download docker-remote openssl ./openssl-download version=1.1.1,type=d
    $
    $ # will download again from server and overwrite the cache
    $ pacco binary download docker-remote openssl ./openssl-download version=1.1.1,type=d  --fresh-download

Get location for pointer to binary cache path
---------------------------------------------
As discussed previously, when you download a new binary, pacco will store it into a cache and
will not re-download if the parameter configuration is the same. Because you
might not want to have the whole copy for each of the project you are working on, pacco actually helps you to refer
to the binary cache location by using ``pacco binary get_location openssl version=1.1.1,type=d`` . And it will output
the directory of the installation
``/Users/kevin/.pacco_cache/__pacco_registry_name=openssl==type=d==version=1.1.1/bin``. To utilize this even better,
you shall not store the value directly in your project build script, but rather you can call the command online::

    $ export OPENSSL_DIR=$(pacco binary get_location openssl version=1.1.1,type=d)

Now you can use the variable ``OPENSSL_DIR`` in your build script as you need.

.. warning::    Note that you shall not store the binary cache path given by pacco since it might get updated and
                the cache may be lost. You shall instead always use the ``get_location`` command.

Next steps
----------
Links to other tutorial.
