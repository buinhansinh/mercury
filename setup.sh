sudo apt-get install git nginx supervisor mysql-server mysql-client mysql-workbench libmysqlclient-dev python-dev build-essentials python-pip python-virtualenv python-zc.buildout
#easy_install -U distribute setuptools
virtualenv --no-site-packages /web/mercury
cd /web/mercury
source bin/activate
python bootstrap.py -d -v 2.1.1
bin/buildout
