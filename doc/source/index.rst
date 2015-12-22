.. wildlife documentation master file, created by
   sphinx-quickstart on Wed Dec  2 15:07:32 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to wildlife's documentation!
====================================

A Flask-based Server Interface to Provide **REST APIs** for `Apache Zookeeper`_


About This Project
------------------

This project **wildlife** (I got this name inspired from the meaning of
`Apache ZooKeeper`_), is a server interface, providing **REST APIs** for
`Apache ZooKeeper`_.

This project now can help you:

* Provide REST APIs (including **GET**/**PUT**/**POST**/**DELETE**) for other micro-services that utilize ZooKeeper cluster for configuration;

* Access all your ZooKeeper Clusters in one portal;

.. _Apache ZooKeeper: https://zookeeper.apache.org/


Important Links
---------------

Support and bug-reports:
https://github.com/dixudx/wildlife/issues?q=is%3Aopen+sort%3Acomments-desc

Project source code: https://github.com/dixudx/wildlife

Project documentation: https://readthedocs.org/projects/wildlife/


How to Use & Configure
----------------------

To **install** wildlife, simply run:

.. code-block:: bash

    $ git clone https://github.com/dixudx/wildlife
    $ cd wildlife
    $ python setup.py install

To **configure** wildlife, simply run:

.. code-block:: bash

    $ cd /{your-site-packages}/wildlife/config
    $ cp wildlife.yml.example wildlife.yml
    $ vim wildlife.yml

And then modify your configurations accordingly.

After the configuration, you can **start** wildlife journey by running:

.. code-block:: bash

    $ python rest.py


Important Notice
----------------

Please do `NOT` use "**list**", "**data**", "**children" and "**acls**"
as znodes names, which have been preserved for the REST APIs usage and may
result in conflicts if using.


Public REST APIs
----------------

.. toctree::
   :maxdepth: 2

   restapis


API Documentation
-----------------

.. toctree::
   :maxdepth: 2

   wildlife.app
   wildlife.manager
   wildlife.rest
   wildlife.wild
   wildlife.wildutils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

