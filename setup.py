try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'digTableExtractor',
    'description': 'digTableExtractor',
    'author': 'Vinay Rao Dandin',
    'url': 'https://github.com/usc-isi-i2/dig-table-extractor',
    'download_url': 'https://github.com/usc-isi-i2/dig-table-extractor',
    'author_email': 'vrdandin@isi.edu',
    'version': '0.2.1',
    'install_requires': ['digExtractor>=0.3.7'],
    # these are the subdirs of the current directory that we care about
    'packages': ['digTableExtractor'],
    'scripts': [],
}

setup(**config)