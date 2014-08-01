# txyam: Yet Another Memcache client
[![Build Status](https://secure.travis-ci.org/bmuller/txyam.png?branch=master)](https://travis-ci.org/bmuller/txyam)

This project is specifically designed for asynchronous [Python Twisted](http://twistedmatrix.com) code to interact with multiple [memcached](http://memcached.org) servers.  A number of other libraries exist, but none of them supported all of the following:

 1. A reconnecting client: if a connection is closed the client should keep trying to reconnect
 1. (Consistent) Partitioning: You should be able to use as many memached servers as you'd like and partition the keys between them, and this should use [consistent hashing](http://en.wikipedia.org/wiki/Consistent_hashing)
 1. Pickling/Compression: You should be able to effortlessly store objects (and have them compressed if you'd like)


## Installation

```bash
pip install txyam
```

## Usage
Usage is pretty straightforward:

```python
# import the client
from txyam.client import YamClient

# create a new client - hosts are either hostnames 
# (default port of 11211 will be used) or host/port tuples
hosts = [ 'localhost', 'otherhost', ('someotherhost', 123) ]
client = YamClient(hosts)

# Run some commands.  You can use all of the typical get/add/replace/etc
# listed at:
# http://twistedmatrix.com/documents/current/api/twisted.protocols.memcache.MemCacheProtocol.html
client.set('akey', 'avalue').addCallback(someHandler)

# Additionally, you can set / add / get picked objects
client.addPickled('anotherkey', { 'dkey': [1, 2, 3] }, compress=True)
client.getPickled('anotherkey', uncompress=True)

# get stats for all servers
def printStats(stats):
    for host, statlist in stats.items():
        print host, statlist['bytes']
client.stats().addCallback(printStats)
```

## Memoizing
You can use txyam to memoize functions/methods.

```python
# assuming "client" is already defined and is a YamClient
@memoize(client)
def mayTakeAWhile(arg, argtwo):
    return takesForever(arg, argtwo)

mayTakeAWhile('blah', 'blah two')
```

After the first time ```mayTakeAWhile``` is called, the results are stored in memcache.  All future
calls just pull the results from memcache.  The function will be memoized based on the function
name and arguments.  The function being memoized can return an object, which will be picked before saving.

## Errors / Bugs / Contact
See [github](http://github.com/bmuller/txyam).
