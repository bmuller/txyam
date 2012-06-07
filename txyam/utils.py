import hashlib

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
