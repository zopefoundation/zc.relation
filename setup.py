##############################################################################
#
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
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
from setuptools import setup, find_packages

long_description = (
    open('src/zc/relation/README.txt').read() + "\n" +
    open('src/zc/relation/CHANGES.txt').read() + "\n")

f = open('TEST_THIS_REST_BEFORE_REGISTERING.txt', 'w')
f.write(long_description)
f.close()

setup(
    name="zc.relation",
    version="1.0",
    packages=find_packages('src'),
    include_package_data=True,
    package_dir= {'':'src'},
    
    namespace_packages=['zc'],

    zip_safe=False,
    author='Gary Poster',
    author_email='gary@zope.com',
    description=open("README.txt").read(),
    long_description=long_description,
    license='ZPL 2.1',
    keywords="zope zope3",
    install_requires=[
        'ZODB3 >= 3.8dev',
        'zope.interface',
        'setuptools',
        
        'zope.testing',
        ],
    extras_require={'test':'zc.relationship'},
    )
