# Requires MySQL installation
# Requires gcc

export PATH=/opt/miniconda2/bin:$PATH
source activate earth
pip install $(cat requirements.txt)
pip install --upgrade .
