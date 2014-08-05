import cPickle
import zlib
import uuid

from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.internet.error import ConnectionDone

from twisted.internet.address import IPv4Address
from twisted.test.proto_helpers import MemoryReactor

from txyam.tests.utils import makeTestConnections
from txyam.client import YamClient, NoServerError
import txyam


class ClientTest(unittest.TestCase):
    # modeled on typical protocol _test method found in twisted,
    # see method in MemCacheTestCase class in twisted/test/test_memcache.py
    # for the source
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
        yclient = YamClient(['one', 'two'], connect=False)
        makeTestConnections(yclient)
        self.assertEqual(yclient.getClient('aaa'), yclient.factories[0].client)
        self.assertEqual(yclient.getClient('foo'), yclient.factories[1].client)

        # now lose first connection
        yclient.factories[0].stopTrying()
        # next line is handled by clientConnectionLost which is called when an actual
        # internet.tcp.Connector has a failed connection
        yclient.factories[0].client = None
        self.assertEqual(yclient.getClient('aaa'), yclient.factories[1].client)
        self.assertEqual(yclient.getClient('foo'), yclient.factories[1].client)


    def test_getClientIsDistributed(self):
        yclient = YamClient(map(str, range(10)), connect=False)
        makeTestConnections(yclient)
        counts = {f.client: 0 for f in yclient.factories}
        for _ in xrange(200):
            client = yclient.getClient(str(uuid.uuid4()))
            counts[client] += 1

        # Expect at least 5% of the values are stored on each client
        for count in counts.values():
            self.assertTrue(count > 10)


    def test_getClientWithConsistentHashing(self):
        """
        Ensure that the client that has a key remains the same if the total number
        of hosts goes up or down.
        """
        yclient = YamClient(map(str, range(9)), connect=False)
        makeTestConnections(yclient)
        self.assertEqual(yclient.factories[6].client, yclient.getClient('sdusdfsdf'))

        yclient = YamClient(map(str, range(10)), connect=False)
        makeTestConnections(yclient)
        self.assertEqual(yclient.factories[6].client, yclient.getClient('sdusdfsdf'))

        yclient = YamClient(map(str, range(11)), connect=False)
        makeTestConnections(yclient)
        self.assertEqual(yclient.factories[6].client, yclient.getClient('sdusdfsdf'))


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
        results = {'one:123': {"foo": "bar", "egg": "spam"}, 'two:456': {"baz": "bar"}}
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


    @inlineCallbacks
    def test_setPickled(self):
        """
        Ensure that pickled object can be stored.
        """
        client = YamClient(['one', 'two'], connect=False)
        transports = makeTestConnections(client)

        # Set a value that should hit first client and not second
        value = cPickle.dumps({'foo': 'bar'}, cPickle.HIGHEST_PROTOCOL)
        send = "set aaa 0 0 %i\r\n%s\r\n" % (len(value), value)
        recv = ["STORED\r\n"]
        yield self._test(client.setPickled("aaa", {'foo': 'bar'}), transports[:1], send, recv, True)
        self.assertEqual(transports[1].value(), "")

        # Set a value that should hit second client and not first
        value = cPickle.dumps({'foo': 'bar'}, cPickle.HIGHEST_PROTOCOL)
        send = "set foo 0 0 %i\r\n%s\r\n" % (len(value), value)
        recv = ["STORED\r\n"]
        transports[0].clear()
        yield self._test(client.setPickled("foo", {'foo': 'bar'}), transports[1:], send, recv, True)
        self.assertEqual(transports[0].value(), "")


    @inlineCallbacks
    def test_setPickledWithCompression(self):
        """
        Ensure that pickled object can be stored with compression.
        """
        client = YamClient(['one', 'two'], connect=False)
        transports = makeTestConnections(client)

        # Set a value that should hit first client and not second, and is gzipped
        value = zlib.compress(cPickle.dumps({'foo': 'bar'}, cPickle.HIGHEST_PROTOCOL))
        send = "set aaa 0 0 %i\r\n%s\r\n" % (len(value), value)
        recv = ["STORED\r\n"]
        d = client.setPickled("aaa", {'foo': 'bar'}, compress=True)
        yield self._test(d, transports[:1], send, recv, True)
        self.assertEqual(transports[1].value(), "")


    @inlineCallbacks
    def test_getPickled(self):
        """
        Ensure that pickled object can be fetched.
        """
        client = YamClient(['one', 'two'], connect=False)
        transports = makeTestConnections(client)

        # Get a value that should hit first client and not second
        value = {'foo': 'bar', 'biz': 'baz'}
        pickled = cPickle.dumps(value, cPickle.HIGHEST_PROTOCOL)
        send = "get aaa\r\n"
        recv = ["VALUE aaa 0 %i\r\n%s\r\nEND\r\n" % (len(pickled), pickled)]
        yield self._test(client.getPickled("aaa"), transports[:1], send, recv, (0, value))
        self.assertEqual(transports[1].value(), "")


    @inlineCallbacks
    def test_getPickledWithCompression(self):
        """
        Ensure that pickled object can be fetched with compression.
        """
        client = YamClient(['one', 'two'], connect=False)
        transports = makeTestConnections(client)

        # Get a value that should hit first client and not second
        value = {'foo': 'bar', 'biz': 'baz'}
        pickled = zlib.compress(cPickle.dumps(value, cPickle.HIGHEST_PROTOCOL))
        send = "get aaa\r\n"
        recv = ["VALUE aaa 0 %i\r\n%s\r\nEND\r\n" % (len(pickled), pickled)]
        d = client.getPickled("aaa", uncompress=True)
        yield self._test(d, transports[:1], send, recv, (0, value))
        self.assertEqual(transports[1].value(), "")


    def test_connect(self):
        txyam.client.reactor = MemoryReactor()
        YamClient(['one', ('two', 123)])
        connection = txyam.client.reactor.connectors[0].getDestination()
        self.assertEqual(connection, IPv4Address('TCP', 'one', 11211))
        connection = txyam.client.reactor.connectors[1].getDestination()
        self.assertEqual(connection, IPv4Address('TCP', 'two', 123))


    def test_disconnect(self):
        client = YamClient(['one', 'two'], connect=False)
        transports = makeTestConnections(client)
        client.disconnect()
        for factory in client.factories:
            self.assertFalse(factory.continueTrying)
        for transport in transports:
            self.assertFalse(transport.connected)
            self.assertTrue(transport.protocol._disconnected)
