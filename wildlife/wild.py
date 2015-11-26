import logging
import exceptions
import yaml
import threading
import time
from wildlife.wildutils import Config, Cluster
from wildlife.manager import ClusterManager


class WildLife(threading.Thread):
    """An Wrapped Class to Handle and Process the Configuration File

    :param conf_path: the configuration yaml file path
    """

    log = logging.getLogger("wildlife.WildLife")

    def __init__(self, conf_path):
        threading.Thread.__init__(self, name='WildLife')
        self.path = conf_path
        self._stopped = False
        self.config = None

    def stop(self):
        self._stopped = True
        for manager in self.config.managers.values():
            manager.stop()

    def run(self):
        while not self._stopped:
            try:
                self.updateConfig()
            except Exception:
                self.log.exception("Exception in WildLife Loop")
            time.sleep(self.config.watermark_sleep)

    def loadConfig(self):
        self.log.debug("Loading configuration from %s", self.path)
        newconfig = Config()

        with open(self.path) as fp:
            config = yaml.load(fp)

        if "wildlife" not in config:
            raise exceptions.KeyError("No key named 'wildlife' "
                                      "in %s" % self.path)

        # Interval between checking if new clusters added
        newconfig.watermark_sleep = config.get("watermark_sleep", 10)

        newconfig.wildlife = set(config["wildlife"])
        newconfig.clusters = dict()
        newconfig.managers = dict()

        if "clusters" not in config:
            raise exceptions.KeyError("No key named 'clusters' "
                                      "in %s" % self.path)
        _clusters = config["clusters"]

        if isinstance(_clusters, dict):
            _clusters = [_clusters]

        unused_clusters = list()
        for _cluster in _clusters:
            _cl_name = _cluster["name"]
            if _cl_name in newconfig.wildlife:
                newconfig.clusters[_cl_name] = self._load_cluster(_cluster)
            else:
                unused_clusters.append(_cl_name)

        if unused_clusters:
            self.log.warning("Clusters %s are not configured in 'wildlife'. "
                             "Inogre them." % unused_clusters)

        available_clusters = set(newconfig.clusters.keys())
        missing_cluters = newconfig.wildlife.difference(available_clusters)
        if missing_cluters:
            err_msg = "Missing Cluster Information for %s" % missing_cluters
            self.log.error(err_msg)
            raise exceptions.AttributeError(err_msg)

        return newconfig

    def _load_cluster(self, cluster):
        self.log.debug("Loading cluster configuration for "
                       "%s" % cluster["name"])
        c = Cluster()
        c.name = cluster["name"]
        c.hosts = cluster.get("hosts")
        if c.hosts is None:
            raise exceptions.AttributeError("Invalid hosts for %s" % c.name)
        c.timeout = float(cluster.get("timeout", 10.0))
        c.default_acl = cluster.get("default_acl", None)
        c.auth_data = cluster.get("auth_data", None)
        c.read_only = cluster.get("read_only", None)
        c.randomize_hosts = cluster.get("randomize_hosts", True)
        return c

    def updateConfig(self):
        self.log.info("Update the config")
        config = self.loadConfig()
        self.reconfigureManagers(config)
        self.setConfig(config)

    def setConfig(self, config):
        self.config = config

    def reconfigureManagers(self, config):
        stop_managers = []
        for manager in config.clusters.values():
            oldmanager = None
            if self.config:
                oldmanager = self.config.managers.get(manager.name)
            if oldmanager and not self._managersEquiv(manager, oldmanager):
                self.log.debug("The information of %s has been "
                               "modified. Will stop the current "
                               "ClusterManager and create a new "
                               "one." % manager.name)
                stop_managers.append(oldmanager)
                oldmanager = None
            if oldmanager:
                config.managers[manager.name] = oldmanager
            else:
                self.log.debug("Creating a new ClusterManager object for %s" %
                               manager.name)
                config.managers[manager.name] = ClusterManager(manager)
                config.managers[manager.name].start()

        for oldmanager in stop_managers:
            oldmanager.stop()

    def _managersEquiv(self, new_manager, old_manager):
        # Check if cluster details have changed

        if (new_manager.randomize_hosts != old_manager.cluster.randomize_hosts
                or new_manager.name != old_manager.cluster.name
                or new_manager.hosts != old_manager.cluster.hosts
                or new_manager.timeout != old_manager.cluster.timeout
                or new_manager.default_acl != old_manager.cluster.default_acl
                or new_manager.auth_data != old_manager.cluster.auth_data
                or new_manager.read_only != old_manager.cluster.read_only):
            return False
        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s: '
                               '(%(threadName)-10s) %(message)s')
    conf_p = "./wildlife.yml"
    wc = WildLife(conf_p)
    wc.start()
