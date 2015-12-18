from wildlife import WildApp
import os
from flask import make_response, request, Response
from wildlife import kz_exceptions
import json
import exceptions
import functools
from kazoo.security import make_acl
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

         "read_only": null,
         "auth_data": null,
         "connection": "CONNECTED",
         "hosts": "10.x.xx.xxx:2181,10.x.xx.xxx:2182",
         "name": "cluster01",
         "timeout": 10.0,
         "randomize_hosts": true,
         "default_acl": null

        }

    """

    _cluster_info = dict()
    _cluster_info.update(app.clusters[cluster_name].__dict__)
    _cluster_info["connection"] = app.managers[cluster_name]._client.state
    resp = Response(json.dumps(_cluster_info),
                    status=200,
                    mimetype="application/json")
    return resp


@app.route("/wildlife/<cluster_name>", methods=["POST"],
           defaults={"znode": None})
@cluster_znode_exception
def cluster_create_znode(cluster_name, znode):
    """create a znode in a specific cluster

    ``POST`` http://[host]:[port]/wildlife/[cluster_name]

    ``Content-Type``: "application/json" or "multipart/form-data"

    ``DATA``:
        {

         "znode_path1": "znode_data1",
         "znode_path2": "znode_data2"

        }

    ``Response`` (string):
        [created_znode_path_list]

    """

    _zclient_manager = app.managers[cluster_name]
    _zclient = _zclient_manager._client
    data = request_data(request)
    real_path_list = list()
    for (_znode, _zdata) in data.items():
        _znodepath = _zclient.create(_znode, value=bytes(_zdata),
                                     makepath=True, acl=None,
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
def cluster_list_children(cluster_name, znode):
    """get the root children of a specific cluster

    ``GET`` http://[host]:[port]/wildlife/[cluster_name]/list

    ``Response`` (string):
        [children_list]

    """

    return cluster_znode_children(cluster_name, "/")


@app.route("/wildlife/<cluster_name>/<path:znode>",
           methods=["GET", "PUT", "DELETE"])
@cluster_znode_exception
def cluster_znode(cluster_name, znode):
    """get the znode data including the znodeStat, update the znode data
    and delete the znode

    ``GET`` http://[host]:[port]/wildlife/[cluster_name]/[znode]

    e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3

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

    ``Response`` (string):
        Successfully Delete Znode [znode] from Cluster [cluster_name].

    """

    _zclient_manager = app.managers[cluster_name]
    _zclient = _zclient_manager._client
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
def cluster_znode_acls(cluster_name, znode):
    """get or update the acls of a znode in a specific cluster


    ``GET`` http://[host]:[port]/wildlife/[cluster_name]/[znode]/acls

    e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3/acls

    ``Response`` (string):
        [ACL(perms=31, acl_list=['ALL'], id=Id(scheme=u'world', id=u'anyone'))]


    ``PUT`` http://[host]:[port]/wildlife/[cluster_name]/[znode]/acls

    ``Content-Type``: "text/plain" or "text/xml"

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

    _zclient_manager = app.managers[cluster_name]
    _zclient = _zclient_manager._client
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
                _scheme = _acl_raw.get("scheme")
                _credential = _acl_raw.get("credential")
                _read = wildutils.get_bool(_acl_raw.get("read", False))
                _write = wildutils.get_bool(_acl_raw.get("write", False))
                _create = wildutils.get_bool(_acl_raw.get("create", False))
                _delete = wildutils.get_bool(_acl_raw.get("delete", False))
                _all = wildutils.get_bool(_acl_raw.get("all", False))

                _acl = make_acl(_scheme, _credential, read=_read,
                                write=_write, create=_create,
                                delete=_delete, all=_all)
                acls_list.append(_acl)

            zstat = _zclient.set_acls(znode, acls_list)
            data = {"znodeStat": wildutils.convert_zstat(zstat)}
            resp = Response(json.dumps(data),
                            status=201,
                            mimetype="application/json")
            return resp


@app.route("/wildlife/<cluster_name>/<path:znode>/data", methods=["GET"])
@cluster_znode_exception
def cluster_znode_data(cluster_name, znode):
    """get only the data of a znode in a specific cluster


    ``GET`` http://[host]:[port]/wildlife/[cluster_name]/[znode]/data

    e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/znode3/data

    ``Response`` (string):
        data for this znode

    """

    zdata_resp = cluster_znode(cluster_name, znode)
    zdata = json.loads(zdata_resp.get_data())
    resp = Response(zdata["data"],
                    status=200,
                    mimetype="text/plain")
    return resp


@app.route("/wildlife/<cluster_name>/<path:znode>/children", methods=["GET"])
@cluster_znode_exception
def cluster_znode_children(cluster_name, znode):
    """get the children of a znode in a specific cluster

    ``GET`` http://[host]:[port]/wildlife/[cluster_name]/[znode]/children

    e.g. http://localhost:5000/wildlife/cluster01/znode1/znode2/children

    ``Response`` (string):
        [children_list]

    """

    _zclient_manager = app.managers[cluster_name]
    _zclient = _zclient_manager._client
    zchildren = _zclient.get_children(znode)
    return make_response(str(zchildren),
                         200)


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
