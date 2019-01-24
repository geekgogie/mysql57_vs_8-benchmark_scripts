#!/usr/bin/env bash

host=$1
port=3306
user="sysbench"
password="MysqP@55w0rd"
table_size=100000
tables=10
rate=20
ps_mode='disable'
threads=1
events=0
time=5
trx=100
path=$PWD

counter=1

echo "thread,cpu" > ${host}-cpu.csv

for i in 16 32 64 128 256 512 1024 2048; 
do 

    threads=$i

    mysql -h $host -e "SHOW GLOBAL STATUS" >> $host-global-status.log
    tmpfile=$path/${host}-tmp${threads}
    touch $tmpfile
    #/usr/bin/ssh -i /home/ubuntu/.ssh/id_rsa ubuntu@${host} "sleep ${time}; top -p \$(pidof mysqld) -b -n1"|grep '%CPU' -A1|awk -v "threads=${threads}" 'NR>1{print threads "," $9}' >> ${host}-cpu-${i}.csv 
    #while [ -f ${host}-tmp${i} ] do /usr/bin/ssh -i /home/ubuntu/.ssh/id_rsa ubuntu@${host} "sleep ${time}; top -p \$(pidof mysqld) -b -n1"|grep '%CPU' -A1|awk -v "threads=${threads}" 'NR>1{print $9}' >> ${host}-cpu-${i}.csv & done
    /bin/bash cpu-checker.sh $tmpfile $host $threads &

    /usr/share/sysbench/oltp_read_write.lua --db-driver=mysql --events=$events --threads=$threads --time=$time --mysql-host=$host --mysql-user=$user --mysql-password=$password --mysql-port=$port --report-interval=1 --skip-trx=on --tables=$tables --table-size=$table_size --rate=$rate --delete_inserts=$trx --order_ranges=$trx --range_selects=on --range-size=$trx --simple_ranges=$trx --db-ps-mode=$ps_mode --mysql-ignore-errors=all run | tee -a $host-sysbench.log

    cp ${tmpfile} ${tmpfile}-bak
    echo "${i},"`cat ${tmpfile} | sort -nr | head -1` >> ${host}-cpu.csv
    unlink ${tmpfile}

    mysql -h $host -e "SHOW GLOBAL STATUS" >> $host-global-status.log
done

python $path/innodb-ops-parser.py $host

mysql -h $host -e "SHOW GLOBAL VARIABLES" >> $host-global-vars.log


