import os, sys, subprocess
import csv

from subprocess import check_call

#import array as arr



def create_csv(ops_v, hostname_ip):
    
    #print ops_v
    path = os.getcwd() + "/"
    csvfile = path + hostname_ip + '-inno-ops.csv'
    
    
    with open(csvfile, "w") as output:
        for row in ops_v:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerow(row)  
    
    output.close()
    


def generate_sysbench_csv(hostname_ip   ):

    path = os.getcwd() + "/"
    csv_filename = path + hostname_ip + "-tps-sysbench.csv"
    sysbench_filename = path + hostname_ip + "-sysbench.log"
    
    
    cmd = ''.join(['cat ', sysbench_filename, '| egrep " cat|threads:|transactions:" | tr -d "\\n" | sed "s/Number of threads: /\\n/g"',
         '| sed "s/\[/\\n/g" | sed "s/[A-Za-z\/]\{1,\}://g"| sed "s/ \.//g"',
         '| awk {\'if(NR > 1){print $1 $3} else {print "threads,tps"}\'}|',
         'sed "s/(/,/g" > ', csv_filename])

    #check_call(cmd, shell=True, executable='/bin/bash')
    os.system(cmd)

    csv_filename = path + hostname_ip + "-transactions-sysbench.csv"
    cmd = ''.join(['cat ', sysbench_filename, '| egrep " cat|threads:|transactions:" | tr -d "\\n" | sed "s/Number of threads: /\\n/g"',
         '| sed "s/\[/\\n/g" | sed "s/[A-Za-z\/]\{1,\}://g"| sed "s/ \.//g"',
         '| awk {\'if(NR > 1){print $1 "," $2} else {print "threads,transactions"}\'} |',
         'sed "s/(/,/g" > ', csv_filename])
    os.system(cmd)

    csv_filename = path + hostname_ip + "-read-write-sysbench.csv"
    cmd = ''.join(['cat ', sysbench_filename, '| egrep " cat|threads:|read:|write:|other:|total:" | tr -d "\\n" | sed "s/Number of threads: /\\n/g"',
         '| sed "s/\[/\\n/g" | sed "s/[A-Za-z\/]\{1,\}://g"| sed "s/ \.//g"',
         '| awk {\'if(NR > 1){print $1",",$2,","$3,",",$4,",",$5} else {print "threads,read,write,other,total"}\'}|',
         'sed "s/(/,/g" > ', csv_filename])
    os.system(cmd)
    
    

def innodb_ops_list_to_csv(a, h): 
    
    #print a
    inno_ops_tbl = []
    row = []
    
    l_deleted = []
    l_inserted = []
    l_read = []
    l_updated = []
    for csv in sorted(a.iterkeys()):
        thd = a[csv]  
        row.append(csv)  
        #print csv    
        if "Innodb_rows_deleted" in thd:
            tmp = thd["Innodb_rows_deleted"]
            l_deleted.append({csv: tmp[1] - tmp[0]})
        
        if "Innodb_rows_inserted" in thd:
            tmp = thd["Innodb_rows_inserted"]
            l_inserted.append({csv: tmp[1] - tmp[0]})
        if "Innodb_rows_read" in thd:
            tmp = thd["Innodb_rows_read"]
            l_read.append({csv: tmp[1] - tmp[0]})
        if "Innodb_rows_updated" in thd:
            tmp = thd["Innodb_rows_updated"]
            l_updated.append({csv:tmp[1] - tmp[0]})
            
    i = 0   
    arr = []
    inno_ops_tbl.append(["tps", "Innodb_rows_deleted", "Innodb_rows_inserted", "Innodb_rows_read", "Innodb_rows_updated"])
    
    for r in row:       
        
        #arr.append(r)
        ##print inno_ops_tbl, r, l_deleted, l_inserted
        #print i, r, l_deleted[i][r]
        arr.append(r)
        arr.append(l_deleted[i][r])
        arr.append(l_inserted[i][r])
        arr.append(l_read[i][r])
        arr.append(l_updated[i][r])
        inno_ops_tbl.append(arr)
        arr = []
        i += 1 
        
    create_csv(inno_ops_tbl, h)
        

def main(host_ip):
    
    status_log=host_ip + "-global-status.log"
    
    a = []
    b = {16:[],32:[],64:[],128:[],256:[],512:[],1024:[],2048:[]}

    ndex = 0
    cur_thd = 16
    inc_deleted = 1

    #innodb_ops=os.system("cat %(status_log)s  |grep 'Innodb_rows_[deleted|inserted|read|updated]' -i | tr '\t' ','" % locals(), "r")
    p = subprocess.Popen("cat %(status_log)s  |grep 'Innodb_rows_[deleted|inserted|read|updated]' -i | tr '\t' ','" % locals(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    for line in p.stdout.readlines():
        a = line.strip().split(',')
        
    
        a[1] = int(a[1])


        if a[0] == "Innodb_rows_deleted":
            if "Innodb_rows_deleted" in b[cur_thd]:
                b[cur_thd]["Innodb_rows_deleted"].append(a[1]) 
            else:        
                if len(b[cur_thd]) > 0 and "Innodb_rows_deleted" in b[cur_thd]:
                    b[cur_thd]["Innodb_rows_deleted"].append(a[1])
                else:
                    #print "only once", cur_thd, b[cur_thd]
                    b[cur_thd] = {a[0]: [a[1]]}
        
        elif a[0] != "Innodb_rows_deleted":
            if a[0] not in b[cur_thd]:
                b[cur_thd].update({a[0]: [a[1]]})
            else:
                b[cur_thd][a[0]].extend([a[1]])
 
        if inc_deleted == 8:
            cur_thd *= 2    
            inc_deleted = 1
        else:
            inc_deleted += 1
 

    #retval = p.wait()
    p.stdout.close()
    

    return b


if __name__ == '__main__':
    
    if (len(sys.argv) < 2):
        raise ValueError("Hostname IP is needed")
        
    host_ip = sys.argv[1];
    
    innodb_ops = main(host_ip)
    
    #print "innodb_ops:", innodb_ops
    innodb_ops_list_to_csv(innodb_ops, host_ip)
    generate_sysbench_csv(host_ip)
    

