import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='rs_limits',
    version='0.1',
    author='Kevin L. Mitchell',
    author_email='kevin.mitchell@rackspace.com',
    description="Rackspace-specific rate-limit preprocessor for turnstile",
    license='Apache License (2.0)',
    py_modules=['rs_limits'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Paste',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        ],
    url='https://github.com/klmitch/rs_limits',
    long_description=read('README.rst'),
    entry_points={
        'console_scripts': [
            'group_class = rs_limits:group_class',
            ],
        },
    install_requires=[
        'argparse',
        'nova_limits',
        'turnstile',
        ],
    )
