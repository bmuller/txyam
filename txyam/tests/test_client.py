from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.internet.error import ConnectionDone

from twisted.internet.address import IPv4Address
from twisted.protocols.memcache import MemCacheProtocol

from txyam.tests.utils import makeTestConnections
from txyam.factory import ConnectingMemCacheProtocol, MemCacheClientFactory
from txyam.client import YamClient, NoServerError


# TODO:
# use http://twistedmatrix.com/trac/browser/tags/releases/twisted-14.0.0/twisted/test/proto_helpers.py#L375
# as reactor

from twisted.internet.base import DelayedCall
DelayedCall.debug = True

class ClientTest(unittest.TestCase):
    def _test(self, d, transports, send, recv, result):
        d.addCallback(self.assertEqual, result)
        for index, transport in enumerate(transports):
            self.assertEqual(transport.value(), send)
            transport.protocol.dataReceived(recv[index])
        return d


    @inlineCallbacks
    def test_sharding_sets(self):
        """
        Ensure that the commands are correctly split by key and sent
        to the correct client.
        """
        client = YamClient(['one', 'two'], connect=False)
        transports = makeTestConnections(client)

        # Set a value that should hit first client and not second
        send = "set aaa 0 0 3\r\nbar\r\n"
        recv = ["STORED\r\n"]
        yield self._test(client.set("aaa", "bar"), transports[:1], send, recv, True)
        self.assertEqual(transports[1].value(), "")

        # Set a value that should hit second client and not first
        send = "set foo 0 0 3\r\nbar\r\n"
        recv = ["STORED\r\n"]
        transports[0].clear()
        yield self._test(client.set("foo", "bar"), transports[1:], send, recv, True)
        self.assertEqual(transports[0].value(), "")


    @inlineCallbacks
    def test_sharding_gets(self):
        """
        Ensure that the commands are correctly split by key and sent
        to the correct client.
        """
        client = YamClient(['one', 'two'], connect=False)
        transports = makeTestConnections(client)

        # Get a value that should hit first client and not second
        send = "get aaa\r\n"
        recv = ["VALUE aaa 0 3\r\nbar\r\nEND\r\n"]
        yield self._test(client.get("aaa"), transports[:1], send, recv, (0, "bar"))
        self.assertEqual(transports[1].value(), "")

        # Get a value that should hit second client and not first
        send = "get foo\r\n"
        recv = ["VALUE foo 0 3\r\nbar\r\nEND\r\n"]
        transports[0].clear()
        yield self._test(client.get("foo"), transports[1:], send, recv, (0, "bar"))
        self.assertEqual(transports[0].value(), "")


    def test_getClient(self):
        """
        Ensure that we can split by key correctly.
        """
        raise NotImplementedError


    @inlineCallbacks
    def test_flushAll(self):
        """
        Ensure that we can flush all servers.
        """
        client = YamClient(['one', 'two'], connect=False)
        transports = makeTestConnections(client)

        send = "flush_all\r\n"
        recv = ["OK\r\n", "OK\r\n"]
        results = [(True, True), (True, True)]
        yield self._test(client.flushAll(), transports, send, recv, results)


    @inlineCallbacks
    def test_no_servers(self):
        """
        Ensure that exception is thrown if no servers are present.
        """
        client = YamClient([], connect=False)
        transports = makeTestConnections(client)

        # flush should be OK with no servers
        send = "flush_all\r\n"
        recv = ["OK\r\n", "OK\r\n"]
        yield self._test(client.flushAll(), transports, send, recv, [])

        # these, however, shoudl be an issue
        self.assertRaises(NoServerError, client.set, "foo", "bar")
        self.assertRaises(NoServerError, client.get, "foo")


    def test_lost_connection(self):
        # now, try with server that has valid transport that
        # has lost its connection
        client = YamClient(['one'], connect=False)
        transports = makeTestConnections(client)
        client.factories[0].stopTrying()

        d1 = client.get("foo")
        d2 = client.get("bar")
        transports[0].loseConnection()

        done = DeferredList([d1, d2], consumeErrors=True)
        def checkFailures(results):
            for success, result in results:
                self.assertFalse(success)
                result.trap(ConnectionDone)
        return done.addCallback(checkFailures)


    @inlineCallbacks
    def test_stats(self):
        """
        Ensure request goes to all servers.
        """
        addrs = [IPv4Address('TCP', 'one', 123), IPv4Address('TCP', 'two', 456)]
        client = YamClient(addrs, connect=False)
        transports = makeTestConnections(client)

        send = "stats\r\n"
        recv = ["STAT foo bar\r\nSTAT egg spam\r\nEND\r\n", "STAT baz bar\r\nEND\r\n"]
        results = {'one:123': {"foo": "bar", "egg": "spam"}, 'two:456': { "baz": "bar" }}
        yield self._test(client.stats(), transports, send, recv, results)


    @inlineCallbacks
    def test_version(self):
        """
        Ensure request goes to all servers.
        """
        addrs = [IPv4Address('TCP', 'one', 123), IPv4Address('TCP', 'two', 456)]
        client = YamClient(addrs, connect=False)
        transports = makeTestConnections(client)

        send = "version\r\n"
        recv = ["VERSION 1.2\r\n", "VERSION 3.4\r\n"]
        results = {'one:123': "1.2", 'two:456': "3.4"}
        yield self._test(client.version(), transports, send, recv, results)


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
