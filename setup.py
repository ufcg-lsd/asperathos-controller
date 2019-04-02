from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='controller',

    version='0.1.0',

    description='Controller component of BIGSEA Asperathos',

    url='',

    author='',
    author_email='',

    license='Apache 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: Apache 2.0',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',

    ],
    keywords='webservice application controllering',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['flask'],

    entry_points={
        'console_scripts': [
            'controller=controller.cli.main:main',
        ],
    },
)
