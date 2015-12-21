.. _restapis:

REST APIs
=========


- `GET`

    - hello page on wildlife REST APIs usages (see `rest.hello
      <./wildlife.rest.html#wildlife.rest.hello>`_ for more details):

      http://[host]:[port]

    - get all clusters info (see `rest.clusters
      <./wildlife.rest.html#wildlife.rest.clusters>`_ for more details):

      http://[host]:[port]/wildlife

    - get the basic information of a specific cluster(see `rest.detail_cluster
      <./wildlife.rest.html#wildlife.rest.detail_cluster>`_ for more details):

      http://[host]:[port]/wildlife/[cluster_name]

    - get the root children of a specific cluster(see `rest.cluster_list_children
      <./wildlife.rest.html#wildlife.rest.cluster_list_children>`_ for  more details):

      http://[host]:[port]/wildlife/[cluster_name]/list

    - get the znode data including the znodeStat(see `rest.cluster_znode
      <./wildlife.rest.html#wildlife.rest.cluster_znode>`_ for more details):

      http://[host]:[port]/wildlife/[cluster_name]/[znode]

      e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3

    - get the acls of a znode in a specific cluster(see `rest.cluster_znode_acls
      <./wildlife.rest.html#wildlife.rest.cluster_znode_acls>`_ for more details):

      http://[host]:[port]wildlife/[cluster_name]/[path:znode]/acls

    - get the children of a znode in a specific cluster(see `rest.cluster_znode_children
      <./wildlife.rest.html#wildlife.rest.cluster_znode_children>`_ for more details):

      http://[host]:[port]/wildlife/[cluster_name]/[znode]/children

      e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/children

    - get only the data of a znode in a specific cluster(see `rest.cluster_znode_data
      <./wildlife.rest.html#wildlife.rest.cluster_znode_data>`_ for more details):

      http://[host]:[port]/wildlife/[cluster_name]/[znode]/data

      e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3/data

- `POST`

    - create a znode in a specific cluster(see `rest.cluster_create_znode
      <./wildlife.rest.html#wildlife.rest.cluster_create_znode>`_ for more details):

      http://[host]:[port]/wildlife/[cluster_name]

- `PUT`

    - update the acls of a znode in a specific cluster(see `rest.cluster_znode_acls
      <./wildlife.rest.html#wildlife.rest.cluster_znode_acls>`_ for more details):

      http://[host]:[port]wildlife/<cluster_name>/<path:znode>/acls

    - update the znode data(see `rest.cluster_znode
      <./wildlife.rest.html#wildlife.rest.cluster_znode>`_ for more details):

      http://[host]:[port]/wildlife/[cluster_name]/[znode]

- `DELETE`

    - delete the znode(see `rest.cluster_znode
      <./wildlife.rest.html#wildlife.rest.cluster_znode>`_ for more details):

      http://[host]:[port]/wildlife/[cluster_name]/[znode]
