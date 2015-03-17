from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = 'locaTE',
    version = '1.0',
    description = 'Discover transposable element insertion sites',
    author = 'Tim Stuart',
    author_email = 'timstuart90@gmail.com',
    url = 'https://github.com/timoast/locaTE',
    py_modules = ['locate'],
    ext_modules = cythonize("merge.pyx")
)