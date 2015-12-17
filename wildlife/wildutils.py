import six


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


def get_bool(v):
    if isinstance(v, bool):
        return v
    elif isinstance(v, six.string_types):
        return v.lower() in ("yes", "true", "t", "1")


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
