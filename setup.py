'''setup module for hostvirtual package'''
from setuptools import setup

VERSION = '0.1'

setup(
    name='hostvirtual',
    version=VERSION,
    install_requires=['requests'],
    description='HostVirtual API Client',
    long_description=open('README.rst').read().strip(),
    author='Shmulik Ladkani',
    author_email='shmulik@nsof.io',
    license=open('LICENSE').read(),
    packages=['hostvirtual'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='hostvirtual netactuate'
)
