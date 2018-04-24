Web interface written on Python (Flask Framework) do deploy Docker containers in HPC infrastructure.

Before start:
sudo -H pip install -U requests
sudo -H pip install -U docker
sudo -H pip install -U flask
sudo -H pip install -U flask_ldap
sudo -H pip install -U flask-bootstrap

Start:
git clone https://github.com/Vsevololod/docker-web.git
cd docker-web
FLASK_APP = app.py
FLASK_ENV = development
FLASK_DEBUG = 0
/usr/bin/python2.7 -m flask run

have a fan)