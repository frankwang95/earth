cd cython
python setup.py build_ext --inplace
cd ..

pip install $(cat requirements.txt)