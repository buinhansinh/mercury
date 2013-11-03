#!/bin/bash

cd /web/mercury
git pull origin
python dropbox.py start
source bin/activate
django rebuild_index --noinput
exec django run_gunicorn