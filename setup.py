#!/usr/bin/env python

from setuptools import setup, find_packages

readme = open('README.md').read()

install_requires = [
    "requests>=2.3.0"
]

setup(
    name='gtail',
    version='0.1.0',
    description='A tool to tail Graylog logs.',
    long_description=readme,
    author='Brandon Vargo',
    url='https://github.com/bvargo/gtail',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'gtail = gtail.gtail:main',
        ]
    }
)
