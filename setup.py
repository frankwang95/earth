from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy as np


exts = cythonize([Extension(
	"pyPreProcPipe",
	sources=[
		"datacollection/landsat/cython/cPreProcPipe.c",
		"datacollection/landsat/cython/pyPreProcPipe.pyx"
	],
	include_dirs=[np.get_include()]
)])


setup(
	name='earth-data-import',
	version='0.0.0',
	author='Frank Wang',
	author_email='fkwang@uchicago.edu',
	packages=find_packages(),
	ext_modules=exts,
	include_package_data=True,
	install_requires=[
		'setuptools-git',
		'mysqlclient',
		'h5py',
		'numpy',
		'requests',
		'cython',
		'scipy',
		'pillow'
	]
)
