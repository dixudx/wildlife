from flask import Flask
from wildlife import WildLife
import logging


class WildApp(Flask):
    """A wrapped class to host flask app and backend WildLife

    Inherit from Flask and Initialize WildLife in __init__

    :param conf_path: the configuration yaml file path
    """

    log = logging.getLogger("wildlife.WildApp")

    def __init__(self, import_name, conf_path,
                 static_path=None, static_url_path=None,
                 static_folder="./static", template_folder="./templates",
                 instance_path=None, instance_relative_config=False):

        super(WildApp,
              self).__init__(import_name, static_path=static_path,
                             static_url_path=static_url_path,
                             static_folder=static_folder,
                             template_folder=template_folder,
                             instance_path=instance_path,
                             instance_relative_config=instance_relative_config)
        self.conf_path = conf_path
        self.managers = None
        self.clusters = None

    def _startWild(self):
        self.log.debug("Start WildLife")
        self.wild = WildLife(self.conf_path)
        try:
            self.wild.updateConfig()
            self.managers = self.wild.config.managers
            self.clusters = self.wild.config.clusters
        except IOError:
            self.log.error("Unable to find configuration file "
                           "%s" % self.conf_path)
        self.wild.start()
