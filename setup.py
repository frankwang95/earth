from setuptools import setup, find_packages


setup(
	name='Distutils',
	version='0.0.0',
	description='earth-learn',
	author='Frank Wang',
	author_email='fkwang@uchicago.edu',
	packages=find_packages(),
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