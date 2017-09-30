.. _install:

############
Installation
############


Install
-------

.. code-block:: python

    import requests as r; exec(r.get('http://bit.ly/get-blackmamba').text)

Copy the above line, paste it into Pythonista interactive prompt and execute it.
Black Mamba will be installed under the ``site-packages-3`` folder.


Update
------

Black Mamba checks for updates automatically. You can disable check for
updates entirely or you can configure time interval.
See :ref:`configuration` section.

Updates are **not** installed automatically. Black Mamba just informs you
about available update. Copy & paste the installation line into Pythonista
interactive prompt and execute it. Latest version will be downloaded and
installed.


PIP
---

If you have `StaSh <https://github.com/ywangd/stash>`_ installed and you do use
``dev`` branch, you can use ``pip`` to install / update Black Mamba. Why ``dev``?
``pip`` in ``master`` does use XML-RPC, which is a legacy PyPI API.
`This pull request <https://github.com/ywangd/stash/pull/269>`_ replaces it with
JSON API and is merged into ``dev`` branch only.

So, you've got ``StaSh`` & ``dev``?

.. code-block:: bash

    pip install blackmamba -d ~/Documents/site-packages-3

How to update Black Mamba via ``pip``? Until `this PR <https://github.com/ywangd/stash/pull/272>`_
will be merged, you have to:

.. code-block:: bash

    pip remove blackmamba
    pip install blackmamba -d ~/Documents/site-packages-3

``pip update`` works, but it removes Black Mamba from ``site-packages-3`` and installs
latest version into the ``site-packages`` folder. Black Mamba is compatible with Python
3 only and we have to keep it in the ``site-packages-3`` folder. Don't use it
and stick with ``pip remove`` and ``pip install``.


Startup
-------

Black Mamba requires from you to put following lines to the
``~/Documents/site-packages-3/pythonista_startup.py`` file:

.. code-block:: python

    #!python3
    import blackmamba

    blackmamba.main()


This is bare minimum. Continue to :ref:`configuration` section to learn how to
tweak Black Mamba.
