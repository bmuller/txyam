# txyam: Yet Another Memcached (YAM) client for Twisted
This project is specifically designed for asynchronous [Python Twisted](http://twistedmatrix.com) code to interact with multiple [memcached](http://memcached.org) servers.  A number of other libraries exist, but none of them supported all of the following:

 1. A reconnecting client: if a connection is closed the client should keep trying to reconnect
 1. Partitioning: You should be able to use as many memached servers as you'd like and partition the keys between them
 1. Pickling/Compression: You should be able to effortlessly store objects (and have them compressed if you'd like)


## Installation

    git clone https://github.com/bmuller/txyam
    cd txyam
    sudo python setup.py install

## Usage

    # import the client
    from txyam.client import YamClient

    # create a new client - hosts are either hostnames (default port of 11211 will be used) or host/port tuples
    hosts = [ 'localhost', 'otherhost', ('someotherhost', 123) ]
    client = YamClient(hosts)

    # Run some commands.  You can use all of the typical get/add/replace/etc
    # listed at http://twistedmatrix.com/documents/current/api/twisted.protocols.memcache.MemCacheProtocol.html
    client.set('akey', 'avalue').addCallback(someHandler)

    # Additionally, you can set / add / get picked objects
    client.addPickled('anotherkey', { 'dkey': [1, 2, 3] }, compress=True)
    client.getPickled('anotherkey', uncompress=True)

## Errors / Bugs / Contact
See [github](http://github.com/bmuller/txyam).