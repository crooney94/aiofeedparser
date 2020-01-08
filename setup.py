from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='aiofeedparser',
    version='1.3.1',

    description='ayncio module using feedparser',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/crooney94/aiofeedparser',

    author='Christopher Rooney',

    author_email='crooney51@qub.ac.uk',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    packages=find_packages(where='aiofeedparser'),

    python_requires='>=3.7',
)
