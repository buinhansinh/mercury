#!/bin/bash

cd /web/mercury
git pull origin
python dropbox.py start
source bin/activate
exec django run_gunicorn