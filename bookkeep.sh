#!/bin/bash

cd /web/mercury
source bin/activate
django bookkeep2 -uadmin
cp logs/*.log /home/terence/Dropbox/logs
