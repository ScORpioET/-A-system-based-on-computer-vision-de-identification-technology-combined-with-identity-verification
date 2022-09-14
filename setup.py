from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("magic.pyx")
)

# use code in cmd : python setup.py build_ext --inplace