from twisted.trial import unittest
from twisted.internet.address import IPv4Address

from txyam.factory import ConnectingMemCacheProtocol, MemCacheClientFactory


class FactoryTest(unittest.TestCase):

    def test_buildProtocol(self):
        f = MemCacheClientFactory()
        addy = IPv4Address('TCP', 'ahost', 1234)
        p = f.buildProtocol(addy, timeOut=123)
        self.assertIsInstance(p, ConnectingMemCacheProtocol)
        self.assertEqual(p.persistentTimeOut, 123)
        self.assertEqual(str(p), "memcache[%s]" % addy)
