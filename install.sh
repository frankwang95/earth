# Requires MySQL installation
# Requires gcc
# Uses Python 3.6 (miniconda3) with clean environment named earth

export PATH=/opt/miniconda2/bin:$PATH
source activate earth
pip install $(cat requirements.txt)
pip install --upgrade .
