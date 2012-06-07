from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks

from utils import YamClientWrapper

class FactoryTest(unittest.TestCase):

    @inlineCallbacks
    def setUp(self):
        self.client = YamClientWrapper()
        yield self.client.setConnection('localhost', 11211)


    @inlineCallbacks
    def test_connection(self):
        yield self.client.set("testkey", '123')
        result = yield self.client.get("testkey")
        self.assertEqual(result[1], '123')
        

    def tearDown(self):
        return self.client.disconnect()
