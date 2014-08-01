from twisted.test.proto_helpers import StringTransportWithDisconnection
from twisted.internet import reactor, protocol
from twisted.protocols.memcache import MemCacheProtocol

from txyam.factory import ConnectingMemCacheProtocol, MemCacheClientFactory


def makeTestConnections(client):
    client.factories = []
    transports = []
    for addr in client.hosts:
        factory = MemCacheClientFactory()
        client.factories.append(factory)
        proto = factory.buildProtocol(addr, timeOut=None)
        transport = StringTransportWithDisconnection()
        transport.protocol = proto
        proto.makeConnection(transport)
        transports.append(transport)
    return transports

