#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(name='dvspec',
      version='0.1',
      description='Ethereum Distributed Validator Specification',
      author='Aditya Asgaonkar',
      author_email='aditya.asgaonkar@ethereum.org',
      url='https://github.com/ethereum/distributed-validator-specs',
      package_dir={'':'src'},
      packages=find_packages(where='src'),
)