from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy as np


exts = cythonize([Extension(
	"pyPreProcPipe",
	sources=[
		"earth/data_import/cython/cPreProcPipe.c",
		"earth/data_import/cython/pyPreProcPipe.pyx"
	],
	include_dirs=[np.get_include()]
)])


setup(
	name='earth-learn',
	version='0.0.0',
	author='Frank Wang',
	author_email='fkwang@uchicago.edu',
	packages=find_packages(),
	ext_modules=exts,
	install_requires=[
		'MySQL-python',
		'h5py',
		'numpy',
		'requests',
		'cython',
		'scipy',
		'pillow'
	]
)