##############################################################################
#
# Copyright (c) 2006-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os

from setuptools import find_packages
from setuptools import setup


def read(path):
    """Read the contents of a file system path."""
    with open(os.path.join(*path.split('/'))) as f:
        return f.read()


setup(
    name="zc.relation",
    version='2.1',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['zc'],
    zip_safe=False,
    author='Gary Poster',
    author_email='zope-dev@zope.dev',
    url="https://github.com/zopefoundation/zc.relation",
    description="Index intransitive and transitive n-ary relationships.",
    long_description="\n\n".join([
        read('src/zc/relation/README.rst'),
        read('src/zc/relation/tokens.rst'),
        read('src/zc/relation/searchindex.rst'),
        read('src/zc/relation/optimization.rst'),
        read('CHANGES.rst'),
    ]),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: Zope Public License',
    ],
    license='ZPL 2.1',
    keywords="zope zope3 relation",
    python_requires='>=3.8',
    install_requires=[
        'BTrees',
        'zope.interface',
        'setuptools',
        'zope.testing',
    ],
    extras_require={'test': [
        'zc.relationship >= 2',
        'ZODB'
    ]},
)
