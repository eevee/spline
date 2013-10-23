import venusian
import zope.interface as zi


class feature_adapter(object):
    def __init__(self, cls, iface):
        self.cls = cls
        self.iface = iface

    def register(self, scanner, name, wrapped):
        config = scanner.config
        config.registry.registerAdapter(wrapped, (self.cls,), self.iface)

    def __call__(self, wrapped):
        venusian.attach(wrapped, self.register, category='spline')
        wrapped = zi.implementer(self.iface)(wrapped)
        return wrapped
