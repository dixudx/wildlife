from wildlife import WildApp
import os
from flask import make_response, request, Response
from wildlife import kz_exceptions
import json
import exceptions
import functools
from wildlife import wildutils


# change to current directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

conf_path = "./config/wildlife.yml"
app = WildApp("wildlife for zookeeper",
              conf_path)


def cluster_znode_exception(func):
    @functools.wraps(func)
    def wrapper(cluster_name, znode):
        try:
            if cluster_name not in app.clusters:
                return make_response("You Haven't Configured Cluster "
                                     "[%s]." % cluster_name,
                                     404)
            return func(cluster_name, znode)
        except (kz_exceptions.ConnectionClosedError,
                kz_exceptions.ConnectionDropped,
                kz_exceptions.ConnectionLoss,
                kz_exceptions.ConnectionLossException):
                return make_response("Connection Exception When Interacts "
                                     "with Cluster [%s].\n" % cluster_name,
                                     408)
        except kz_exceptions.NoNodeException:
            return make_response("Cannot Find Znode [%s] in Cluster "
                                 "[%s].\n" % (znode, cluster_name),
                                 404)
        except kz_exceptions.InvalidACLException:
            return make_response("Invalid ACLs on Accessing Znode [%s] in "
                                 "Cluster [%s].\n" % (znode, cluster_name),
                                 401)
        except kz_exceptions.NoAuthException:
            return make_response("Please Provide ACLs to Access Znode [%s] in "
                                 "Cluster [%s].\n" % (znode, cluster_name),
                                 401)
        except kz_exceptions.ZookeeperError:
            return make_response("ZooKeeper Server Error on Interacting with "
                                 "Cluster [%s].\n" % cluster_name,
                                 406)
        except exceptions as excp:
            return make_response("Unable to Handle this Request with "
                                 "exception: %s.\n" % excp,
                                 500)
    return wrapper


@app.route("/")
def hello():
    """This is the hello page on wildlife REST APIs usages


    ``GET``
        hello page on wildlife REST APIs usages: \
        http://[host]:[port]

        get all clusters info: \
        http://[host]:[port]/wildlife

        get the basic information of a specific cluster: \
        http://[host]:[port]/wildlife/[cluster_name]

        get the root children of a specific cluster: \
        http://[host]:[port]/wildlife/[cluster_name]/list

        get the znode data including the znodeStat: \
        http://[host]:[port]/wildlife/[cluster_name]/[znode]
        e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3

        get the acls of a znode in a specific cluster: \
        http://[host]:[port]wildlife/[cluster_name]/[znode]/acls

        get the children of a znode in a specific cluster: \
        http://[host]:[port]/wildlife/[cluster_name]/[znode]/children
        e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/children

        get only the data of a znode in a specific cluster: \
        http://[host]:[port]/wildlife/[cluster_name]/[znode]/data
        e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3/data


    ``POST``
        create a znode in a specific cluster: \
        http://[host]:[port]/wildlife/[cluster_name]


    ``PUT``
        update the znode data: \
        http://[host]:[port]/wildlife/[cluster_name]/[znode]


    ``DELETE``
        delete the znode: \
        http://[host]:[port]/wildlife/[cluster_name]/[znode]

    """

    usage_msg = "<br/>\n".join(["Welcome to WildLife: The REST APIs for "
                                "ZooKeeper!<br/>",
                                hello.__doc__.replace("\n", "<br/>\n")])

    return make_response(usage_msg, 200)


@app.route("/wildlife", methods=["GET"])
def clusters():
    """get all clusters

    ``GET`` http://[host]:[port]/wildlife

    ``Response`` (json data):
        {

         "clusters": [cluster_list]

        }

    """

    data = {"clusters": app.clusters.keys()}

    resp = Response(json.dumps(data),
                    status=200,
                    mimetype="application/json")

    return resp


@app.route("/wildlife/<cluster_name>", methods=["GET"],
           defaults={"znode": None})
@cluster_znode_exception
def detail_cluster(cluster_name, znode):
    """get the basic information of a specific cluster

    ``GET`` http://[host]:[port]/wildlife/[cluster_name]

    ``Response`` (json data):
        {

         "connection": "CONNECTED",
         "hosts": "10.x.xx.xxx:2181,10.x.xx.xxx:2182",
         "name": "cluster01",
         "timeout": 10.0,
         "randomize_hosts": true

        }

    """

    _cluster_info = dict()
    _cluster_info.update(app.clusters[cluster_name].__dict__)
    _cluster_info.pop("auth_data", None)
    _cluster_info["connection"] = app.managers[cluster_name]._client.state
    resp = Response(json.dumps(_cluster_info),
                    status=200,
                    mimetype="application/json")
    return resp


@app.route("/wildlife/<cluster_name>", methods=["POST"],
           defaults={"znode": None})
@cluster_znode_exception
def cluster_create_znode(cluster_name, znode, headers=None):
    """create a znode in a specific cluster

    ``POST`` http://[host]:[port]/wildlife/[cluster_name]

    ``Headers`` (optional, if you need want to create these znodes
        with an acl):
         {

          "scheme": "digest",
          "credential": "user1,password1",
          "read": True,
          "write": False,
          "create": False,
          "delete": False,
          "admin": True,
          "all": False

         }

    ``Content-Type``: "application/json" or "multipart/form-data"

    ``DATA``:
        {

         "znode_path1": "znode_data1",
         "znode_path2": "znode_data2"

        }

    ``Response`` (string):
        [created_znode_path_list]

    """

    _zclient = get_client(cluster_name,
                          headers or request.headers)
    acl_config = wildutils.ACLConfig(headers or request.headers)
    data = request_data(request)
    real_path_list = list()
    for (_znode, _zdata) in data.items():
        _znodepath = _zclient.create(_znode,
                                     value=bytes(_zdata),
                                     makepath=True,
                                     acl=acl_config.make_acl(),
                                     ephemeral=False,
                                     sequence=False)
        real_path_list.append(_znodepath)
    resp = Response(str(real_path_list),
                    status=200,
                    mimetype="text/plain")
    return resp


@app.route("/wildlife/<cluster_name>/list", methods=["GET"],
           defaults={"znode": None})
@cluster_znode_exception
def cluster_list_children(cluster_name, znode, headers=None):
    """get the root children of a specific cluster

    ``GET`` http://[host]:[port]/wildlife/[cluster_name]/list

    ``Headers`` (optional, if the znode you are accessing needs an acl):
         {

          "scheme": "digest",
          "credential": "user1,password1"

         }

    ``Response`` (string):
        [children_list]

    """

    return cluster_znode_children(cluster_name,
                                  "/",
                                  headers=headers or request.headers)


@app.route("/wildlife/<cluster_name>/<path:znode>",
           methods=["GET", "PUT", "DELETE"])
@cluster_znode_exception
def cluster_znode(cluster_name, znode, headers=None):
    """get the znode data including the znodeStat, update the znode data
    and delete the znode

    ``GET`` http://[host]:[port]/wildlife/[cluster_name]/[znode]


    e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3

    ``Headers`` (optional, if the znode you are accessing needs an acl):
         {

          "scheme": "digest",
          "credential": "user1,password1"

         }

    ``Response`` (json data):
        {

         "znodeStat":
            {

             "ephemeralOwner": 0,
             "dataLength": 19,
             "mtime": 1448608198011,
             "czxid": 8589936224,
             "pzxid": 8589936224,
             "ctime": 1448608198011,
             "mzxid": 8589936224,
             "numChildren": 0,
             "version": 0,
             "aversion": 0,
             "cversion": 0

            },

         "data": "data for this znode"

        }


    ``PUT`` http://[host]:[port]/wildlife/[cluster_name]/[znode]

    ``Content-Type``: "text/plain;charset=UTF-8", "application/json",
        "text/xml" or "multipart/form-data"

    ``Headers`` (optional, if the znode you are accessing needs an acl):
         {

          "scheme": "digest",
          "credential": "user1,password1"

         }

    ``DATA``

    ``Response`` (json data):
        {

         "znodeStat":
            {

             "ephemeralOwner": 0,
             "dataLength": 27,
             "mtime": 1449033225435,
             "czxid": 8589936438,
             "pzxid": 8589936439,
             "ctime": 1449033225435,
             "mzxid": 8589936438,
             "numChildren": 0,
             "version": 0,
             "aversion": 0,
             "cversion": 1

            },

         "data": "updated data for this znode"

        }


    ``DELETE`` http://[host]:[port]/wildlife/[cluster_name]/[znode]

    ``Headers`` (optional, if the znode you are accessing needs an acl):
         {

          "scheme": "digest",
          "credential": "user1,password1"

         }

    ``Response`` (string):
        Successfully Delete Znode [znode] from Cluster [cluster_name].

    """

    _zclient = get_client(cluster_name,
                          headers or request.headers)
    if request.method == "GET":
        zdata = _zclient.get(znode)
        data = {"data": zdata[0],
                "znodeStat": wildutils.convert_zstat(zdata[1])}
        resp = Response(json.dumps(data),
                        status=200,
                        mimetype="application/json")
        return resp
    elif request.method == "PUT":
        _new_data = request_data(request)
        zdata = _zclient.set(znode, _new_data)
        data = {"data": _new_data,
                "znodeStat": wildutils.convert_zstat(zdata)}
        resp = Response(json.dumps(data),
                        status=201,
                        mimetype="application/json")
        return resp
    elif request.method == "DELETE":
        _zclient.delete(znode, recursive=False)
        return make_response("Successfully Delete Znode [%s] from "
                             "Cluster [%s].\n" % (znode, cluster_name),
                             202)


@app.route("/wildlife/<cluster_name>/<path:znode>/acls",
           methods=["GET", "PUT"])
@cluster_znode_exception
def cluster_znode_acls(cluster_name, znode, headers=None):
    """get or update the acls of a znode in a specific cluster


    ``GET`` http://[host]:[port]/wildlife/[cluster_name]/[znode]/acls

    e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3/acls

    ``Headers`` (optional, if the znode you are accessing needs an acl):
         {

          "scheme": "digest",
          "credential": "user1,password1"

         }

    ``Response`` (string):
        [ACL(perms=31, acl_list=['ALL'], id=Id(scheme=u'world', id=u'anyone'))]


    ``PUT`` http://[host]:[port]/wildlife/[cluster_name]/[znode]/acls

    ``Content-Type``: "text/plain" or "text/xml"

    ``Headers`` (optional, if the znode you are accessing needs an acl):
         {

          "scheme": "digest",
          "credential": "user1,password1"

         }

    ``DATA``:

        [
         {"scheme": "digest",
          "credential": "user1,password1",
          "read": True,
          "write": False,
          "create": False,
          "delete": False,
          "admin": False,
          "all": False
         },
         {"scheme": "digest",
          "credential": "user2,password2",
          "all": True
         }
        ]

    Parameters Explanations:
        scheme: The scheme to use. I.e. digest.
        credential: A colon separated username, password.
            The password should be hashed with the scheme specified.
        write (bool): Write permission.
        create (bool): Create permission.
        delete (bool): Delete permission.
        admin (bool): Admin permission.
        all (bool): All permissions.

    ``Response`` (string):
        [created_znode_path_list]

    """

    _zclient = get_client(cluster_name,
                          headers or request.headers)
    if request.method == "GET":
        acls = _zclient.get_acls(znode)[0]
        return make_response(str(acls),
                             200)

    if request.method == "PUT":
        if request.content_type not in ["text/plain", "text/xml"]:
            return make_response("The Content-Type is not supported. "
                                 "Please use text/plain or text/xml. \n",
                                 406)
        else:
            acls_raw = eval(request.data)
            acls_list = list()
            for _acl_raw in acls_raw:
                _acl_config = wildutils.ACLConfig(_acl_raw)
                acls_list.append(_acl_config.make_acl())

            zstat = _zclient.set_acls(znode, acls_list)
            data = {"znodeStat": wildutils.convert_zstat(zstat)}
            resp = Response(json.dumps(data),
                            status=201,
                            mimetype="application/json")
            return resp


@app.route("/wildlife/<cluster_name>/<path:znode>/data", methods=["GET"])
@cluster_znode_exception
def cluster_znode_data(cluster_name, znode, headers=None):
    """get only the data of a znode in a specific cluster


    ``GET`` http://[host]:[port]/wildlife/[cluster_name]/[znode]/data

    e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3/data

    ``Headers`` (optional, if the znode you are accessing needs an acl):
         {

          "scheme": "digest",
          "credential": "user1,password1"

         }

    ``Response`` (string):
        data for this znode

    """

    zdata_resp = cluster_znode(cluster_name,
                               znode,
                               headers=headers)
    zdata = json.loads(zdata_resp.get_data())
    resp = Response(zdata["data"],
                    status=200,
                    mimetype="text/plain")
    return resp


@app.route("/wildlife/<cluster_name>/<path:znode>/children", methods=["GET"])
@cluster_znode_exception
def cluster_znode_children(cluster_name, znode, headers=None):
    """get the children of a znode in a specific cluster

    ``GET`` http://[host]:[port]/wildlife/[cluster_name]/[znode]/children

    e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/children

    ``Headers`` (optional, if the znode you are accessing needs an acl):
         {

          "scheme": "digest",
          "credential": "user1,password1"

         }

    ``Response`` (string):
        [children_list]

    """

    _zclient = get_client(cluster_name,
                          headers or request.headers)
    zchildren = _zclient.get_children(znode)
    return make_response(str(zchildren),
                         200)


def get_client(cluster_name, headers):
    zcl_mngr = app.managers[cluster_name]
    acl_config = wildutils.ACLConfig(headers)
    if not acl_config.check_acl():
        zclient = zcl_mngr._client
    else:
        from kazoo.client import KazooClient
        auth_data = (acl_config.scheme, acl_config.credential)
        zclient = KazooClient(hosts=zcl_mngr.cluster.hosts,
                              timeout=zcl_mngr.cluster.timeout,
                              auth_data=auth_data,
                              randomize_hosts=zcl_mngr.cluster.randomize_hosts,
                              logger=zcl_mngr.log)

    return zclient


def request_data(request):
    if request.content_type == "application/x-www-form-urlencoded":
        data = request.form
    elif "multipart/form-data" in request.content_type:
        data = request.form
    elif request.content_type == "text/plain":
        data = request.data
    elif request.content_type == "application/json":
        data = request.json
    elif request.content_type == "text/xml":
        data = request.data
    else:
        data = request.data

    if not data:
        return "".join(request.environ["wsgi.input"].readlines())
    return data


def main(host="localhost"):
    app._startWild()
    app.run(host=host)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s: '
                               '(%(threadName)-10s) %(message)s')
    main(host="0.0.0.0")
