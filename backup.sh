#!/bin/bash

NOW=$(date +"%Y-%m-%d-%H-%M")
mysqldump -uroot -ppassw0rd mercury > mercury.db
7z a mercury.db.7z mercury.db
rm mercury.db
mv mercury.db.7z /home/terence/Dropbox
