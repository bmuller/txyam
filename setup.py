#!/usr/bin/env python
try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

setup(
    name="txyam",
    version="0.1",
    description="Yet Another Memcached (YAM) client for Twisted.",
    author="Brian Muller",
    author_email="bamuller@gmail.com",
    license="MIT",
    url="http://github.com/bmuller/txyam",
    packages=["txyam", "txyam.tests"],
    requires=["twisted.protocols.memcache"]
)
