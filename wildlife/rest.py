from wildlife import WildApp
import os
from flask import jsonify, make_response, Response
from wildlife import kz_exceptions
import logging


# change to current directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

conf_path = "./config/wildlife.yml"
app = WildApp("wildlife for zookeeper",
              conf_path)


@app.route("/")
def hello():
    return make_response("Welcome to WildLife: The REST API for ZooKeeper!",
                         200)


@app.route("/wildlife", methods=["GET"])
def clusters():
    return make_response(jsonify({"clusters": app.clusters.keys()}),
                         200)


@app.route("/wildlife/<cluster_name>", methods=["GET"])
def detail_cluster(cluster_name):
    return make_response(jsonify(app.clusters[cluster_name].__dict__),
                         200)


@app.route("/wildlife/<cluster_name>/<znode>", methods=["GET"])
def cluster_znode(cluster_name, znode):
    _zclient_manager = app.managers[cluster_name]
    _zclient = _zclient_manager._client
    try:
        zdata = _zclient.get(znode)
        return make_response(jsonify({"data": zdata[0],
                                      "znodeStat": convert_zstat(zdata[1])
                                      }),
                             200)
    except kz_exceptions.NoNodeError:
        return make_response("Cannot Find Znode %s in Cluster"
                             "%s.\n" % (znode, cluster_name),
                             404)


@app.route("/wildlife/<cluster_name>/<znode>/data", methods=["GET"])
def cluster_znode_data(cluster_name, znode):
    _zclient_manager = app.managers[cluster_name]
    _zclient = _zclient_manager._client
    print znode
    try:
        zdata = _zclient.get(znode)
        return make_response(zdata[0],
                             200)
    except:
        pass


@app.route("/wildlife/<cluster_name>/<znode>/children", methods=["GET"])
def cluster_znode_children(cluster_name, znode):
    _zclient_manager = app.managers[cluster_name]
    _zclient = _zclient_manager._client
    zchildren = _zclient.get_children(znode)
    return make_response(str(zchildren),
                         200)


def convert_zstat(znodeStat):
    return {"czxid": znodeStat.czxid,
            "mzxid": znodeStat.mzxid,
            "ctime": znodeStat.ctime,
            "mtime": znodeStat.mtime,
            "version": znodeStat.version,
            "cversion": znodeStat.cversion,
            "aversion": znodeStat.aversion,
            "ephemeralOwner": znodeStat.ephemeralOwner,
            "dataLength": znodeStat.dataLength,
            "numChildren": znodeStat.numChildren,
            "pzxid": znodeStat.pzxid}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s: '
                               '(%(threadName)-10s) %(message)s')
    app.run()
