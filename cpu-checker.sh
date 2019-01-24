#!/usr/bin/env bash
tmpfile=$1
host=$2
thread=$3

while [ -f $tmpfile ];
do
    /usr/bin/ssh -i /home/ubuntu/.ssh/id_rsa ubuntu@${host} "sleep 1; top -p \$(pidof mysqld) -b -n1"|grep '%CPU' -A1|awk 'NR>1{print $9}' >> $tmpfile
done
