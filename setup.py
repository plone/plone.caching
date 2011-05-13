import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.txt')
    + '\n' +
#    read('plone', 'caching', 'README.txt')
#    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )

setup(name='plone.caching',
      version=version,
      description="Zope 2 integration for z3c.caching",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone http caching',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.caching',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.caching [zcml]',
          'plone.registry',
          'zope.interface',
          'zope.component',
          'zope.i18nmessageid',
          'zope.schema',
          'plone.transformchain',
          'five.globalrequest',
          'Zope2 >= 2.12.4',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
