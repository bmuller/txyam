from twisted.internet import reactor, protocol
from twisted.protocols.memcache import MemCacheProtocol
from twisted.internet.defer import inlineCallbacks

from txyam.client import YamClient

class YamClientWrapper(YamClient):
    def __init__(self):
        pass

    
    def setConnection(self, host, port):
        def save(connection):
            self.connection = connection
            return self
        
        clientCreator = protocol.ClientCreator(reactor, MemCacheProtocol)        
        return clientCreator.connectTCP(host, port).addCallback(save)


    def getClient(self, key):
        # we only have one connection
        return self.connection


    def getActiveConnections(self):
        # we only have one connection
        return [self.connection]


    def disconnect(self):
        return self.connection.transport.loseConnection()
