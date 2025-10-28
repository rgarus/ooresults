Delopment workflow
==================

.. only:: html

   .. contents::
      :depth: 2


This section describes commands for cloning, editing, analysing, formatting, testing,
creating and publishing the ooresults software for the Linux operating system.


Cloning the software
--------------------

.. code-block::

   mkdir <git-local>
   cd <git-local>
   git clone https://github.com/rgarus/ooresults.git .



Installing the software in editable mode
----------------------------------------

.. code-block::

   python -m venv <venv>
   cd <git-local>
   <venv>/bin/python -m pip install -e .[test]



Formatting the Python source code with black and isort
------------------------------------------------------

For isort we use the following configuration parameters,
defined in pyproject.toml in section [tool.isort]:

.. code-block::

   [tool.isort]
   profile = "black"
   force_single_line = "true"
   lines_after_imports = 2

Format the code:

.. code-block::

   python -m pip install black isort
   
   cd <git-local>
   python -m isort .
   python -m black .


   
Analysing the Python source code with Ruff
------------------------------------------

We use Ruff linter for the static code analysis of the Python source code.
The rules used are defined in pyproject.toml in the sections
[tool.ruff.lint] and [tool.ruff.lint.isort].

.. code-block::

   python -m pip install ruff
   
   cd <git-local>
   python -m ruff check



Testing the ooresults software
------------------------------

The software should be tested for the following Python versions:

- Python 3.9
- Python 3.10
- Python 3.11


.. code-block::

   cd <git-local>
   <venv>/bin/python -m pytest tests
   <venv>/bin/python -m pytest webtests



Testing with docker
-------------------

We use docker to check if the unit tests run successfully with all
supported Python versions. A dockerfile and a bash script are stored
in <git-local>/tests/docker. To execute the tests run the following
script:

.. code-block::

   cd <git-local>
   tests/docker/tests.sh



Building the documentation
--------------------------

.. code-block::

   python -m venv <venv-sphinx>
   <venv-sphinx>/bin/python -m pip install sphinx sphinx-multiproject
   
   cd <git-local>/docs
   source <venv-sphinx>/bin/activate
   
   make html
   make latexpdf
   
   PROJECT=dev make html
   PROJECT=dev make latexpdf



Building an ooresults release
-----------------------------

Edit and change the version number in the following files:

- <git-local>/docs/conf.py
- <git-local>/pyproject.toml
- <git-local>/CHANGELOG.rst



Build the release:

.. code-block::

   python -m venv <venv-build>
   <venv-build>/bin/python -m pip install build setuptools twine 
   
   cd <git-local>
   <venv-build>/bin/python -m build



Publishing the release
----------------------

For uploading the build results to https://pypi.org use
(during upload use __token__ as username):

.. code-block::

   cd <git-local>
   <venv-build>/bin/python -m twine check dist/*
   <venv-build>/bin/python -m twine upload dist/*

For uploading the build results to https://test.pypi.org use
(during upload use __token__ as username):

.. code-block::

   cd <git-local>
   <venv-build>/bin/python -m twine check dist/*
   <venv-build>/bin/python -m twine --repository testpypi upload dist/*
