pip install $(cat requirements.txt)

cd earth/data_import/cython
python setup.py build_ext --inplace
cd ../../..

python setup.py install