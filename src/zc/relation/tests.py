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
"""Relation index tests
"""
import doctest
import unittest

import zope.testing.module


def setUp(test):
    zope.testing.module.setUp(test, 'zc.relation.DOCTESTS')


def tearDown(test):
    db = test.globs.get('db')
    if db is not None:
        import transaction
        transaction.abort()
        db.close()
    zope.testing.module.tearDown(test)


def test_suite():
    res = unittest.TestSuite((
        doctest.DocFileSuite(
            'README.rst',
            setUp=setUp,
            tearDown=tearDown,
        ),
        doctest.DocFileSuite(
            'tokens.rst',
            setUp=setUp,
            tearDown=tearDown,
        ),
        doctest.DocFileSuite(
            'searchindex.rst',
            setUp=setUp,
            tearDown=tearDown,
        ),
        doctest.DocFileSuite(
            'optimization.rst',
            setUp=setUp,
            tearDown=tearDown,
        ),
    ))
    return res
