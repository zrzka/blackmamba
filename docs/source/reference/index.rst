.. _reference:

#####################
Black Mamba Reference
#####################

:Release: |version|
:Date: |today|


Versioning
==========

Black Mamba does use `semantic versioning <http://semver.org/>`_ since version 1.0.0.
Given a version number ``MAJOR.MINOR.PATCH``:

* ``MAJOR`` version is incremented if there're incompatible API changes,
* ``MINOR`` version is incremented if there's a new functionality in a backwards-compatible manner,
* ``PATCH`` version is incremented if there're backwards-compatible bug fixes.

Black Mamba does not use additional labels for pre-release and build metadata as extensions
to the ``MAJOR.MINOR.PATCH`` format.


Modules
=======

Following modules are considered to be the API for Black Mamba from the versioning point
of view. Black Mamba includes lot of other modules, but it's not recommended to use them,
because they can break even if ``MAJOR`` is not incremented.

.. toctree::
   :maxdepth: 1

   blackmamba
   blackmamba.log
   blackmamba.system
   blackmamba.uikit.keyboard
