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
from __future__ import print_function

import os

from setuptools import find_packages
from setuptools import setup

# generic helpers primarily for the long_description
try:
    import docutils
except ImportError:
    def validateReST(text):
        return ''
else:
    import docutils.utils
    import docutils.parsers.rst
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

    def validateReST(text):
        doc = docutils.utils.new_document('validator')
        # our desired settings
        doc.reporter.halt_level = 5
        doc.reporter.report_level = 1
        stream = doc.reporter.stream = StringIO()
        # docutils buglets (?)
        doc.settings.tab_width = 2
        doc.settings.pep_references = doc.settings.rfc_references = False
        doc.settings.trim_footnote_reference_space = None
        # and we're off...
        parser = docutils.parsers.rst.Parser()
        parser.parse(text, doc)
        return stream.getvalue()


def text(*args, **kwargs):
    # note: distutils explicitly disallows unicode for setup values :-/
    # http://docs.python.org/dist/meta-data.html
    tmp = []
    for a in args:
        if a.endswith('.rst'):
            f = open(os.path.join(*a.split('/')))
            tmp.append(f.read())
            f.close()
            tmp.append('\n\n')
        else:
            tmp.append(a)
    if len(tmp) == 1:
        res = tmp[0]
    else:
        res = ''.join(tmp)
    out = kwargs.get('out')
    if out is True:
        out = 'TEST_THIS_REST_BEFORE_REGISTERING.rst'
    if out:
        f = open(out, 'w')
        f.write(res)
        f.close()
        report = validateReST(res)
        if report:
            print(report)
            raise ValueError('ReST validation error')
    return res
# end helpers; below this line should be code custom to this package


setup(
    name="zc.relation",
    version='1.1',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['zc'],
    zip_safe=False,
    author='Gary Poster',
    author_email='gary@zope.com',
    url="https://github.com/zopefoundation/zc.relation",
    description=text("README.rst"),
    long_description=text('src/zc/relation/README.rst',
                          'src/zc/relation/tokens.rst',
                          'src/zc/relation/searchindex.rst',
                          'src/zc/relation/optimization.rst',
                          'src/zc/relation/CHANGES.rst'),
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: Zope Public License',
    ],
    license='ZPL 2.1',
    keywords="zope zope3 relation",
    install_requires=[
        'ZODB3 >= 3.8dev',
        'zope.interface',
        'setuptools',
        'six',
        'zope.testing',
    ],
    extras_require={'test': 'zc.relationship >= 2.0c1'},
)
