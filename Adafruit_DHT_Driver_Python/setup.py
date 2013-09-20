#!/usr/bin/env python
# -*- coding:utf-8 -*-

from distutils.core import setup, Extension

dht_mod = Extension('dhtreader',
                    include_dirs = ['.'],
                    libraries = ['bcm2835'],
                    sources = ['dhtreader.c'])

setup (name = 'dhtreader',
       version = '1.0',
       description = 'Python library to interface with dht sensors',
       ext_modules = [dht_mod])
