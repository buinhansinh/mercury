#!/bin/bash

cd /web/mercury
git pull origin
python dropbox.py start
source bin/activate
django update_index
exec django run_gunicorn