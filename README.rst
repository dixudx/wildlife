wildlife
========

.. image:: https://readthedocs.org/projects/wildlife/badge/?version=latest
    :target: https://readthedocs.org/projects/wildlife

.. image:: https://api.travis-ci.org/dixudx/wildlife.svg?branch=master
    :target: https://github.com/dixudx/wildlife

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

To **configure** wildlife, simply:

.. code-block:: bash

    $ cd /{your-site-packages}/wildlife/config
    $ cp wildlife.yml.example wildlife.yml

And then modify your configurations accordingly.

After the configuration, you can **start** wildlife journey by running:

.. code-block:: bash

    $ python rest.py


Important Notice
----------------

Please do `NOT` use "**list**", "**data**", "**children**" and "**acls**"
as znodes names, which have been preserved for the REST APIs usage and may
result in conflicts if using.


REST APIs
---------

For more detailed inforamtion, please visit http://wildlife.readthedocs.org/en/latest/restapis.html

- `GET`

    - hello page on wildlife REST APIs usages:

      http://[host]:[port]

    - get all clusters info:

      http://[host]:[port]/wildlife

    - get the basic information of a specific cluster:

      http://[host]:[port]/wildlife/[cluster_name]

    - get the root children of a specific cluster:

      http://[host]:[port]/wildlife/[cluster_name]/list

    - get the znode data including the znodeStat:

      http://[host]:[port]/wildlife/[cluster_name]/[znode]

      e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3

    - get the acls of a znode in a specific cluster:

      http://[host]:[port]wildlife/[cluster_name]/[znode]/acls

    - get the children of a znode in a specific cluster:

      http://[host]:[port]/wildlife/[cluster_name]/[znode]/children

      e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/children

    - get only the data of a znode in a specific cluster:

      http://[host]:[port]/wildlife/[cluster_name]/[znode]/data

      e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3/data

- `POST`

    - create a znode in a specific cluster:

      http://[host]:[port]/wildlife/[cluster_name]

- `PUT`

    - update the acls of a znode in a specific cluster:

      http://[host]:[port]wildlife/<cluster_name>/<path:znode>/acls

    - update the znode data:

      http://[host]:[port]/wildlife/[cluster_name]/[znode]

- `DELETE`

    - delete the znode:

      http://[host]:[port]/wildlife/[cluster_name]/[znode]
