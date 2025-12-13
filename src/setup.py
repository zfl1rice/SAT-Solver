from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        ["src/dpll_cy/core.pyx"],
        compiler_directives={"language_level": "3"},
    ),
)
