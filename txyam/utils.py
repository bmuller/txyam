import hashlib

from twisted.internet import defer

def signedInt(n):
    n = n & 0xffffffff
    return ((1 << 31) & n) and (~n + 1) or n


def ketama(key):
    """
    MD5-based hashing algorithm used in consistent hashing scheme
    to compensate for servers added/removed from memcached pool.

    Copied from dpnova / txmemcache found at:
    https://github.com/dpnova/txmemcache/blob/master/txmemcache/hash.py
    """
    d = hashlib.md5(key).digest()
    c = signedInt
    h = c((ord(d[3])&0xff) << 24) | c((ord(d[2]) & 0xff) << 16) | c((ord(d[1]) & 0xff) << 8) | c(ord(d[0]) & 0xff)
    return h


def deferredDict(d):
    """
    Just like a C{defer.DeferredList} but instead accepts and returns a C{dict}.

    @param d: A C{dict} whose values are all C{Deferred} objects.

    @return: A C{DeferredList} whose callback will be given a dictionary whose
    keys are the same as the parameter C{d}'s and whose values are the results
    of each individual deferred call.
    """
    if len(d) == 0:
        return defer.succeed({})

    def handle(results, names):
        rvalue = {}
        for index in range(len(results)):
            rvalue[names[index]] = results[index][1]
        return rvalue

    dl = defer.DeferredList(d.values())
    return dl.addCallback(handle, d.keys())


class Memoizer:
    """
    Class to handle memoizing functions.  Not meant to be instantiated
    by any code other than the C{memoize} function.
    """
    def __init__(self, client):
        self.client = client


    def memoize(self, func):
        self.func = func
        return self.caller


    def caller(self, *args, **kwargs):
        self.key = hashlib.sha1(repr(self.client) + repr(args) + repr(kwargs)).hexdigest()
        d = self.client.getPickled(self.key)
        return d.addCallback(self.handleResult, args, kwargs)


    def saveResult(self, result):
        d = self.client.setPickled(self.key, result)
        return d.addCallback(lambda _: result)


    def handleResult(self, result, args, kwargs):
        if result[1] is None:
            d = defer.maybeDeferred(self.func, *args, **kwargs)
            return d.addCallback(self.saveResult)
        return defer.succeed(result[1])


def memoize(client):
    """
    Memoize a function.  Used like this:

    @memoize(yamclient)
    def rememberable(one, two):
        return takesForever(one, two)

    Where C{yamclient} is an instance of C{txyam.YamClient} in the
    decorator.  The function will be memoized based on the function
    name and arguments.  The function being memoized can return an
    object, which will be picked before saving.
    """
    return Memoizer(client).memoize
