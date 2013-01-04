from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log
from twisted.protocols.memcache import MemCacheProtocol

class ConnectingMemCacheProtocol(MemCacheProtocol):
    def connectionMade(self):
        self.factory.connectionMade()


class MemCacheClientFactory(ReconnectingClientFactory):
    initialDelay = 0.1
    protocol = ConnectingMemCacheProtocol
    noisy = True

    def __init__(self):
        self.client = None
        self.addr = None
        self.deferred = Deferred()


    def buildProtocol(self, addr):
        self.client = self.protocol()
        self.addr = addr
        self.client.factory = self
        self.resetDelay()
        return self.client


    def clientConnectionLost(self, connector, reason):
        log.msg("Lost connection to %s - %s" % (self.addr, reason))
        self.client = None
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)


    def clientConnectionFailed(self, connector, reason):
        log.msg("Connection failed to %s - %s" % (self.addr, reason))
        self.client = None
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


    def connectionMade(self):
        if self.deferred is not None:
            self.deferred.callback(self)
            self.deferred = None
