from setuptools import setup, find_packages
import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = read('src/z3c/saconfig/README.txt') + '\n' + read('CHANGES.txt')

setup(name='z3c.saconfig',
      version = '0.12dev',
      description="Minimal SQLAlchemy ORM session configuration for Zope",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Zope3',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Database',
                   ],
      keywords='zope relational sqlalchemy component integration',
      author='Martijn Faassen',
      author_email='faassen@startifact.com',
      url='http://pypi.python.org/pypi/z3c.saconfig',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
          'zope.sqlalchemy>=0.4',
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
