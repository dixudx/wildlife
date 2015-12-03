.. _restapis:

REST APIs
=========


- `GET`

    - get all clusters info:

      http://[host]:[port]/wildlife

    - get the basic information of a specific cluster:

      http://[host]:[port]/wildlife/[cluster_name]

    - get the root children of a specific cluster:

      http://[host]:[port]/wildlife/[cluster_name]/list

    - get the znode data including the znodeStat:

      http://[host]:[port]/wildlife/[cluster_name]/[znode]

      e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3

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

    - update the znode data:

      http://[host]:[port]/wildlife/[cluster_name]/[znode]

- `DELETE`

    - delete the znode:

      http://[host]:[port]/wildlife/[cluster_name]/[znode]
