Delopment workflow
==================

.. only:: html

   .. contents::
      :depth: 2


This section describes commands to clone, edit, format, test, build and publish the ooresults software for operating system Linux.



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



Formating the Python source code
--------------------------------

.. code-block::

   python -m pip install black
   
   cd <git-local>
   python -m black .



Testing the ooresults software
------------------------------

The software should be tested for the following Python versions:

- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11


.. code-block::

   cd <git-local>
   <venv>/bin/python -m pytest tests
   <venv>/bin/python -m pytest webtests



Building the documentation
--------------------------

.. code-block::

   python -m venv <venv-sphinx>
   <venv-sphinx>/bin/python -m pip install sphinx sphinx-multiproject
   
   cd <git-local>
   source <venv-sphinx>/bin/activate
   
   make html
   make latexpdf
   
   PROJECT=dev make html
   PROJECT=dev makr latexpdf



Building an ooresults release
-----------------------------

Edit and change the version number in the following files

- <git-local>/docs/source/conf.py
- <git-local>/.readthedocs.yaml
- <git-local>/pyproject.toml


Build the release

.. code-block::

   python -m venv <venv-build>
   <venv-build>/bin/python -m pip install build setuptools twine 
   
   cd <git-local>
   <venv-build>/bin/python -m build



Publishing the release
----------------------

For uploading to https://pypi.org use (during upload use __token__ as username):

.. code-block::

   <venv-build>/bin/python -m twine check dist/*
   <venv-build>/bin/python -m twine upload dist/*
   
For uploading to https://test.pypi.org use (during upload use __token__ as username):

.. code-block::

   <venv-build>/bin/python -m twine check dist/*
   <venv-build>/bin/python -m twine --repository testpypi upload dist/*
