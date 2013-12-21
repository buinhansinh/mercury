sudo apt-get install p7zip-full nginx supervisor mysql-server mysql-client mysql-workbench libmysqlclient-dev python-dev build-essential python-pip python-virtualenv python-zc.buildout
virtualenv --no-site-packages /web/mercury
cd /web/mercury
mkdir logs
source bin/activate
easy_install -U distribute setuptools
pip install eventlet
python bootstrap.py
bin/buildout
sudo cp supervisor.conf /etc/supervisor/conf.d/mercury.conf
sudo supervisorctl update
sudo cp nginx.conf /etc/nginx/sites-available/mercury.conf
ln -s /etc/nginx/sites-available/mercury.conf /etc/nginx/sites-enabled/mercury.conf
sudo service nginx restart
