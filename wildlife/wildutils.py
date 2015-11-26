class ConfigValue(object):
    """Base Class for Configuration
    """

    pass


class Config(ConfigValue):
    """Configuration Class for WildLife
    """

    pass


class Cluster(ConfigValue):
    """Configuration Class for ZooKeeper Cluster
    """

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__,
                            str(self))

    def __str__(self):
        return self.name
