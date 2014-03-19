#!/bin/bash

cd /web/mercury
source bin/activate
django bookkeep2 -uadmin --year 2013
