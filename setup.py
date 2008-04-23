from setuptools import setup, find_packages


long_description = (
    open('src/zc/relation/README.txt').read() + "\n" +
    open('src/zc/relation/CHANGES.txt').read() + "\n")

f = open('TEST_THIS_REST_BEFORE_REGISTERING.txt', 'w')
f.write(long_description)
f.close()

setup(
    name="zc.relation",
    version="1.0b1",
    packages=find_packages('src'),
    include_package_data=True,
    package_dir= {'':'src'},
    
    namespace_packages=['zc'],

    zip_safe=False,
    author='Zope Project',
    author_email='zope3-dev@zope.org',
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
