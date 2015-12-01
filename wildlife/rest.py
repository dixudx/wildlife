from wildlife import WildApp
import os
from flask import jsonify, make_response
from wildlife import kz_exceptions
import json
import exceptions
import functools


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

        except exceptions:
            return make_response("Unable to Handle this Request.\n",
                                 500)
    return wrapper


@app.route("/")
def hello():
    """hello"""

    return make_response("Welcome to WildLife: The REST API for ZooKeeper!\n",
                         200)


@app.route("/wildlife", methods=["GET"])
def clusters():
    """get all clusters"""

    return make_response(jsonify({"clusters": app.clusters.keys()}),
                         200)


@app.route("/wildlife/<cluster_name>", methods=["GET"],
           defaults={"znode": None})
@cluster_znode_exception
def detail_cluster(cluster_name, znode):
    """get the basic information of a specific cluster"""

    _cluster_info = dict()
    _cluster_info.update(app.clusters[cluster_name].__dict__)
    _cluster_info["connection"] = app.managers[cluster_name]._client.state
    return make_response(jsonify(_cluster_info),
                         200)


@app.route("/wildlife/<cluster_name>/<znode>", methods=["GET"])
@cluster_znode_exception
def cluster_znode(cluster_name, znode):
    """get the znode data including the znodeStat"""

    _zclient_manager = app.managers[cluster_name]
    _zclient = _zclient_manager._client
    zdata = _zclient.get(znode)
    return make_response(jsonify({"data": zdata[0],
                                  "znodeStat": convert_zstat(zdata[1])
                                  }),
                         200)


@app.route("/wildlife/<cluster_name>/<znode>/data", methods=["GET"])
@cluster_znode_exception
def cluster_znode_data(cluster_name, znode):
    """get only the data of a znode in a specific cluster"""

    zdata = cluster_znode(cluster_name, znode)
    zdata = json.loads(zdata)
    return make_response(zdata["data"],
                         200)


@app.route("/wildlife/<cluster_name>/<znode>/children", methods=["GET"])
@cluster_znode_exception
def cluster_znode_children(cluster_name, znode):
    """get the children of a znode in a specific cluster"""

    _zclient_manager = app.managers[cluster_name]
    _zclient = _zclient_manager._client
    zchildren = _zclient.get_children(znode)
    return make_response(str(zchildren),
                         200)


def convert_zstat(znodestat):
    return {"czxid": znodestat.czxid,
            "mzxid": znodestat.mzxid,
            "ctime": znodestat.ctime,
            "mtime": znodestat.mtime,
            "version": znodestat.version,
            "cversion": znodestat.cversion,
            "aversion": znodestat.aversion,
            "ephemeralOwner": znodestat.ephemeralOwner,
            "dataLength": znodestat.dataLength,
            "numChildren": znodestat.numChildren,
            "pzxid": znodestat.pzxid}


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s: '
                               '(%(threadName)-10s) %(message)s')
    app.run()
