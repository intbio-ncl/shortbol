from distutils.core import setup
import setuptools

setup(name='rdfscript',
      version='0.0',
      description='A domain specific language for easily describing RDF data.',

      author='Lewis Grozinger',

      author_email='lgrozinger2@ncl.ac.uk',

      url='https://github.com/lgrozinger/rdfscript',

      packages=['rdfscript', 'extensions'],

      py_modules=['run'],

      install_requires=['rdflib', 'lxml', 'requests', 'ply', 'pathlib', 'pysbolgraph']
)
