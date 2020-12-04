from setuptools import setup
from os import path

# Get the contents of the MD readme for a description
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='matrix_enum',
    version='1.1.0',
    url='https://github.com/klaviyo/matrix_enum',
    author='Klaviyo',
    description='Data structure for multi-dimensional enums',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    author_email='maintainers@klaviyo.com',
    packages=['matrix_enum'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    install_requires=[
        'six>=1.12',
        'enum34>=1.1.6;python_version<"3.4"',
    ],
    extras_require={
        'dev': [
            'tox~=3.13',
        ],
    },
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    keywords='enum',
)
