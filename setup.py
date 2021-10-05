"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='pyretroprint', 
    version='0.1.8',
    description='PyRetroPrint: Dot-Matrix Emulation for our Bleak Dystopian Future!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rubeon/pyretroprint',
    author='rubeon',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    
    keywords='retro, glue, atari, emulation',
    package_dir={'pyretroprint': 'pyretroprint'},
    packages=find_packages(where='.'),
    python_requires='>=3.6, <4',
    install_requires=['pycairo'],
    entry_points={  # Optional
        'console_scripts': [
            'pyretroprint=pyretroprint.pyretroprint:main',
        ],
    },
    
    project_urls={ 
        'Bug Reports': 'https://github.com/rubeon/pyretroprint/issues',
        'Source': 'https://github.com/rubeon/pyretroprint/',
    }
)