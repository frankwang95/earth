# Requires MySQL Server installation
sudo apt-get install mysql-server
sudo apt-get install libmysqlclient-dev

# Requires gcc
sudo apt-get install  gcc

# Uses Python 3.6 (miniconda3) with clean environment named earth
source activate earth

# Install Python dependencies
pip install $(cat requirements.txt)
pip install --upgrade .
