pip install $(cat requirements.txt)


cd cython
python setup.py build_ext --inplace
cd ..
