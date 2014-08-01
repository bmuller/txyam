#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="txyam",
    version="1.0",
    description="Yet Another Memcached (YAM) client for Twisted.",
    author="Brian Muller",
    author_email="bamuller@gmail.com",
    license="MIT",
    url="http://github.com/bmuller/txyam",
    packages=find_packages(),
    requires=["twisted.protocols.memcache", "hash_ring"],
    install_requires=['twisted>=12.0','hash_ring>=1.3.1']
)
