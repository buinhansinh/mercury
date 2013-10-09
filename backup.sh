NOW=$(date +"%Y-%m-%d-%H-%M")
mysqldump -uroot -ppassw0rd mercury > mercury.dump
7z a mercury-$NOW.7z mercury.dump
rm mercury.dump
