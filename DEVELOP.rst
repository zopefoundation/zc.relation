To develop this package from source:

- check out the software from the repository

- ``cd`` to the checkout

- Ideally with a clean, non-system python, run
  ``python bootstrap.py``

- run ``./bin/buildout``

To run tests, run *both* of the following:

- ``./bin/test``: this tests zc.relation alone

- ``./bin/testall``: this tests zc.relation and zc.relationship, to make sure
  that zc.relation changes do not break zc.relationship tests.

Changes should be documented in CHANGES.rst *in the package*.

Before making a release that registers the software to PyPI, run the
`longtest` command of the ``zest.releaser`` package to check for errors
in the ``long_description``.

Once this works, go ahead and ``./bin/py setup.py sdist upload``.
