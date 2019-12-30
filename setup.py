#!python3

from pip._internal.req import parse_requirements
from setuptools import setup, find_packages


setup(
    name='Validate and upload to Jenkins',
    version="1.0.0",
    python_requires='>3.7.4',
    packages=find_packages(),
    install_requires=[i.req.name for i in parse_requirements('requirements.txt', session='hack')],
)

