# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='gnucash-categorizer',
    version='0.1.0',
    description='Tool for moving uncategorized Gnucash transactions into the correct accounts.',
    long_description=readme,
    author='David Seddon',
    author_email='david@seddonym.me',
    url='https://github.com/seddonym/gnucash-categorizer',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
