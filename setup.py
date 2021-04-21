from setuptools import setup
from Cython.Build import cythonize

setup(
    name='PDI app',
    ext_modules=cythonize("./src/trent_procesador.pyx"),
    zip_safe=False,
)