##############
Advanced Guide
##############

Editing registry and binary parameters
**************************************

In the :ref:`Quick Start` we already learned how to add remote, add registry and add binary. However, some questions are still left, such as:
* How to edit the parameter list of an existing registry?
* How do we edit the value of the parameter of a binary?

Editing registry parameters
===========================
If we check the help for registry, we can find::

    $ pacco registry -h

      pacco registry add           Add registry to remote.
      pacco registry binaries      List binaries of a registry from a specific remote.
      pacco registry list          List registries of a remote.
      pacco registry param_add     Add new parameter with default value to the binaries.
      pacco registry param_list    List params of a registry.
      pacco registry param_remove  Remove an existing parameter from all binaries.
      pacco registry remove        Remove a registry from a specific remote.

    Pacco registry commands. Type 'pacco registry <command> -h' for help

So turns out we have access to the two commands ``param_add`` and ``param_remove``. With ``param_add`` you can add a new parameter list to this registry setting and all binaries under this registry. The new parameter will have the value of the default value you provide assigned to the binaries. If you don't provide the default value, it will be assigned the value ``"default"``. Similarly, ``param_remove`` will delete a parameter from this registry and every binary within this registry. However, if this causes two binary to be indistinguishable from the rest of the parameter, this action will be aborted. For example, let say you have two binaries with values ``{'os': 'osx', 'version': '1.1'}`` and ``{'os': 'linux', 'version': '1.1'}``. If we remove the ``os``, it will cause the two binary to be indistinguishable with only the parameter ``version``, thus this action is rejected by pacco.

These command may look line not powerful; you can't directly reassign a new parameter list without manually deleting and adding everything. But this was done purposefully to ease the synchronization with the package binaries. There will be no strange edge cases though the steps might look redundant.

Changing the value of binary parameter
======================================
In the previous section, we learn that ``param_add`` will automatically assign a default value to each binary. How can we change that value? ::

    $ pacco binary -h

      pacco binary download      Download from a specified or default remote. Will use cache if exists unless enforced by '--fresh-download' flag
      pacco binary get_location  Get the path to the cache location for the binary.
      pacco binary reassign      Change the assignment of a binary to a new one
      pacco binary remove        Remove a binary from a remote
      pacco binary upload        Upload binary to a specified remote and store it to cache.

    Pacco binary commands. Type 'pacco binary <command> -h' for help

    $ pacco binary reassign -h

    usage: pacco binary reassign [-h]
                             remote_name registry_name old_settings
                             new_settings

    positional arguments:
      remote_name    remote name
      registry_name  registry name
      old_settings   old settings (e.g. os=linux,version=2.1.0,type=debug
      new_settings   new settings (e.g. os=osx,version=2.1.1,type=debug

    optional arguments:
      -h, --help     show this help message and exit

So it's as simple as providing the old settings in the correct format and giving the new settings. It will check whether that change will cause any clash (two binary with the exact same settings, i.e., indistinguishable), and it will abort if that happens.

Default Remotes
***************

These commands:

#. ``pacco remote list_default``
#. ``pacco remote set_default``
#. ``pacco binary download default``
#. ``pacco binary get_location``

is related with this notion of "default remotes". The default remotes basically means the list of remote that is set as default for the attempt to download binaries. It is important to note that other command will not use the concept of default remote.

Maybe it is easier to see directly how the command will work to understand the default remote.

List default remotes
====================
We start with something simple, ``pacco remote list_default`` will list out for you the default remotes that is currently registered in your local client. The list is stored in some internal config file (in this version, it is in the file ``~/.pacco_config``. But as always you should not rely on implementation detail.) The order it appears represent the order of trial for the download attempt.

Set default remotes
===================
You can set the default remote list in your local client using the command ``pacco remote set_default [remote1] [remote2] ...``. If you want to set it to be empty, you can just do ``pacco remote set_default`` without additional tokens. However, empty default remote list will mean any attempt to use the default remote will result in failure.

Download from default remotes
=============================
Sometimes you want to have some order of priority of where you shall get the binaries. Let say you have 2 server, one with high availability but low bandwidth, and the other with low availability but high bandwidth. You want to download from the high bandwidth but fallback to the high availability server if the high bandwidth is not available. This can be done by using default remote list, setting the high bandwidth server as first priority then the high availability as the second. Then when you are downloading the binary, instead of specifying the remote name, you just specify "default" as the remote name. However, if all of the remotes does not contain the matched registry name and binary settings, it will give up and raise an error.

Use default remote if not found in cache
========================================
As discussed in :ref:`Get location for pointer to binary cache path`, we can use ``pacco binary get_location`` command to get the binary cache path. But, if it is not found in the cache, it will attempt to download from the default remotes. It will also download from the default remotes if the flag ``--fresh-download`` is provided.

Cloning a remote
****************

How can we clone a remote? Or can we? Unfortunately, as discussed in :ref:`Centralized`, clone is not supported natively in Pacco for now. The workaround for now is that you can just download what you need from a remote server and put it to your local server. The clone functionality, other than adding complexity, will also defeat the initial purpose of developing pacco to "download only what you need" (in contrast to the current solution we have in our team previously).

Alternatives to cloning for decentralization
********************************************

Probably we don't want to clone a whole remote locally, but how about uploading/syncing between remotes? Such that we (as a local client) will have our standalone remote that can be sync up (at the granularity of binary object) with other remotes. This is nice to have. But turns out that that's what the cache is all about. You have kind of like your own server (though it might not look like a fully functioning server), but it does the job such that you can upload from your cache to a remote (by downloading from the cache then uploading it), and download to the cache from a server. Yes, it is not the exact same as decentralized but it does the basic need. If you think that we need this specific architecture, just raise up an issue in the Github and you can also provide some design ideas.
