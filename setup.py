#!/usr/bin/env python

from distutils.core import setup

setup(name='python-ucsvlog',
      version='0.2.1',
      description='logging in ucsv format',
      author='Alexander Lyabah',
      author_email='alexander@lyabah.com',
      packages=['ucsvlog','ucsvlog.fields'],
      url='https://github.com/oduvan/python-ucsvlog',
      package_dir={'ucsvlog': 'ucsvlog','ucsvlog.fields':'ucsvlog/fields'}
)
