from distutils.core import setup
import setuptools

setup(name='shortbol',
      version='0.0',
      description='A domain specific language for SBOL',

      author='Various',

      packages=['rdfscript', 'extensions'],

      py_modules=['run'],

      install_requires=['rdflib', 'lxml', 'requests', 'ply', 'pathlib', 'pysbolgraph']
)
