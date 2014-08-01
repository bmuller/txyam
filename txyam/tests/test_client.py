from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks
from twisted.test.proto_helpers import StringTransportWithDisconnection

from twisted.protocols.memcache import MemCacheProtocol
from txyam.factory import ConnectingMemCacheProtocol




class ClientTest(unittest.TestCase):
    def test_sharding(self):
        """
        Ensure that the commands are correctly split by key and sent
        to the correct client.
        """
        raise NotImplementedError


    def test_getClient(self):
        """
        Ensure that we can split by key correctly.
        """
        raise NotImplementedError


    def test_flushAll(self):
        """
        Ensure that we can flush all servers.
        """
        raise NotImplementedError


    def test_no_servers(self):
        """
        Ensure that exception is thrown if no servers are present.
        """
        raise NotImplementedError


    def test_stats(self):
        """
        Ensure request goes to all servers.
        """
        raise NotImplementedError


    def test_version(self):
        """
        Ensure request goes to all servers.
        """
        raise NotImplementedError


    def test_addPickled(self):
        """
        Ensure that pickled object can be stored, both with and without
        compression.
        """
        raise NotImplementedError


    def test_getPickled(self):
        """
        Ensure that pickled object can be fetched, both with and without
        compression.
        """
        raise NotImplementedError

    
    def test_connection(self):
        self.proto = MemCacheProtocol()
        self.transport = StringTransportWithDisconnection()
        self.transport.protocol = self.proto
        self.proto.makeConnection(self.transport)

        d = self.proto.get("foo")
        self.assertEqual(self.transport.value(), "get foo\r\n")
        d.addCallback(self.assertEqual, (0, "bar"))
        self.proto.dataReceived("VALUE foo 0 3\r\nbar\r\nEND\r\n")
        return d
