#!/usr/bin/env python

from distutils.core import setup
try:  # for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements
    from pip.download import PipSession


install_requires = parse_requirements('requirements.txt', session=PipSession())
dependencies = [str(package.req) for package in install_requires]

setup(name='hydra-flock-drone',
      version='0.0.1',
      description='A simulation for HYDRA: Drone API',
      author='W3C HYDRA development group',
      author_email='collective@hydraecosystem.org',
      url='https://github.com/HTTP-APIs/hydra-flock-demo',
      install_requires=dependencies
      )
