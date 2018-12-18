from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = read('src/z3c/saconfig/README.rst') + '\n' + read('CHANGES.rst')

setup(name='z3c.saconfig',
      version='0.16.0.dev0',
      description="Minimal SQLAlchemy ORM session configuration for Zope",
      long_description=long_description,
      # Get more strings from https://pypi.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Zope :: 3',
                   'Framework :: Zope :: 4',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Database',
                   ],
      keywords='zope relational sqlalchemy component integration',
      author='Martijn Faassen',
      author_email='faassen@startifact.com',
      url='https://github.com/zopefoundation/z3c.saconfig/',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
          'zope.sqlalchemy>=0.5',
          'zope.interface',
          'zope.component',
          'zope.hookable',
          'zope.security',
          'zope.event',
          'zope.configuration',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      extras_require = dict(
              test = ['zope.testing'],
              ),
      )
