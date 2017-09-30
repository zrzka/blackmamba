.. _development:

###########
Development
###########


Style
=====

There's no defined style for development. Just stick with the same style you see
in other blackmamba modules.


Pull requests
=============

Pull requests must pass ``flake8`` checks:

.. code-block:: shell

    flake8 . --count --select=E901,E999,F821,F822,F823 --show-source --statistics
    flake8 . --count --max-complexity=10 --max-line-length=127 --statistics


Pull requests must pass tests:

.. code-block:: shell

    PYTHONPATH=. pytest tests


Consult `.travis.yml <https://github.com/zrzka/blackmamba/blob/master/.travis.yml>`_ for more details.


Existing issues
===============

Let me know if you'd like to work on `something <https://github.com/zrzka/blackmamba/issues>`_.
To avoid situation where I already started working on it.


New ideas
=========

I'm open to new ideas as well. Please, `file an issue <https://github.com/zrzka/blackmamba/issues>`_
first, we can discuss it and then you can implement it.
