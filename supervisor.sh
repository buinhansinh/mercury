#!/bin/bash

cd /web/mercury
git pull origin
source bin/activate
django run_gunicorn