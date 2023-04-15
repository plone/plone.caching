from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = "2.0.0"

long_description = read("README.rst") + "\n" + read("CHANGES.rst") + "\n"

setup(
    name="plone.caching",
    version=version,
    description="Zope 2 integration for z3c.caching",
    long_description=long_description,
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone http caching",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.caching",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["plone"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "z3c.caching [zcml]",
        "plone.registry",
        "zope.interface",
        "zope.component",
        "zope.i18nmessageid",
        "zope.schema",
        "plone.transformchain",
    ],
    extras_require={
        "test": [
            "plone.testing",
        ],
    },
    entry_points="""
      # -*- Entry points: -*-
      """,
)
