from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy as np

exts = cythonize([Extension(
	"pyPreProcPipe",
	sources=["cPreProcPipe.c", "pyPreProcPipe.pyx"],
	include_dirs=[np.get_include()]
)])

setup(
    ext_modules = exts,
)