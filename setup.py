import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2.1'

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst')
    + '\n'
    )

setup(name='plone.caching',
      version=version,
      description="Zope 2 integration for z3c.caching",
      long_description=long_description,
      # Get more strings from
      # https://pypi.org/classifiers/
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 5.0",
          "Framework :: Plone :: 5.1",
          "Framework :: Plone :: 5.2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='plone http caching',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://pypi.org/project/plone.caching',
      license='GPL',
      packages=find_packages(),
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
          'Zope2 >= 2.12.4',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
