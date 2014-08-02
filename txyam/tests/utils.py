from twisted.test.proto_helpers import StringTransportWithDisconnection

from txyam.factory import MemCacheClientFactory


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
