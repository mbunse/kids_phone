#!/bin/python

from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='kids_phone',
      version='0.1.dev1',
      description='Raspberry Pi project for a SIP or VoIP phone for children.',
      keywords='raspberry pi raspi voip sip phone',
      url='https://github.com/mbunse/kids_phone',
      author='Moritz Bunse',
      author_email='mbunse@hotmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[],
      python_requires='2.7.*'
      )