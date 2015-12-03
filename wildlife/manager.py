import threading
from kazoo.client import KazooClient
import logging


class ClusterManager(threading.Thread):

    log = logging.getLogger("wildlife.ClusterManager")

    def __init__(self, cluster):
        super(ClusterManager, self).__init__(name=cluster.name)
        self.cluster = cluster
        self.name = self.cluster.name
        self._client = None
        self._stopped = False

    def stop(self):
        self._stopped = True
        self._client.stop()

    def _getClient(self):
        self.log.debug("Get KazooClient for %s" % self.name)
        return KazooClient(hosts=self.cluster.hosts,
                           timeout=self.cluster.timeout,
                           default_acl=self.cluster.default_acl,
                           auth_data=self.cluster.auth_data,
                           read_only=self.cluster.read_only,
                           randomize_hosts=self.cluster.randomize_hosts,
                           logger=self.log)

    def run(self):
        self._client = self._getClient()
        while not self._stopped:
            if not self._client.connected:
                try:
                    self._client.stop()
                    self._client.start()
                except Exception as excp:
                    self.log.exception("Exception of %s: "
                                       "%s" % (self.cluster.name,
                                               excp))
