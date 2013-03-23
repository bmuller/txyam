#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="txyam",
    version="0.4",
    description="Yet Another Memcached (YAM) client for Twisted.",
    author="Brian Muller",
    author_email="bamuller@gmail.com",
    license="MIT",
    url="http://github.com/bmuller/txyam",
    packages=find_packages(),
    requires=["twisted.protocols.memcache"],
    install_requires=['twisted>=12.0']
)
