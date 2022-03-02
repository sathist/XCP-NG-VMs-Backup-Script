import subprocess as sp
import os
from datetime import datetime
import logging

print("\n XCP-NG Xenserver Backup Automation Script")
logging.basicConfig(filename="/var/log/xenserverbkp/xenserver-backuper.log", format='%(asctime)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

try:
    sp.getoutput(
        "xe vm-list is-control-domain=false is-a-snapshot=false power-state=running | grep -i uuid | sed 's/uuid[^\:]*\:\ //g' > vm_uuid_list")
    sp.getoutput(
        "xe vm-list is-control-domain=false is-a-snapshot=false power-state=running | grep -i name-label | sed 's/name-label[^\:]*\:\ //g' > vm_name_list")
    now = datetime.now()
    start_time = now.strftime("%Y-%m-%d")
    # print(start_time)

    with open('vm_uuid_list', 'r') as f:
        hostuuid = f.read().splitlines()
        # with open('vm_name_list','r+') as fi:
        # lines=fi.read().splitlines()
        # print(hostname)
    with open('vm_name_list', 'r') as fi:
        lines = fi.read().replace(' ', '')
    with open('vm_name_list', 'w') as fi:
        fi.write(lines)
    with open('vm_name_list', 'r') as fi:
        hostname = fi.read().splitlines()

    print(hostname)
    logger.info(hostname)
    i = 0
    print("VM UUID LIST fetched \n")

    for uuid in hostuuid:
        # print ("\033[92m  *** \033[00m")
        take_snapshot = ("Selecting to take snapshot - \033[92m VM Name:" + hostname[i] + " VM uuid:"+uuid + "\033[00m")
        logger.info(take_snapshot)
        print(take_snapshot)
        snapid = sp.getoutput('xe vm-snapshot new-name-label='+hostname[i]+' uuid='+uuid)
        snap_details = ("Snapshot taken from " + hostname[i]+" - snapshot ID: "+snapid)
        logger.info(snap_details)
        print(snap_details)
        print("\n Creating backup directories with current date on the path /mnt/nas")
        sp.getoutput('mkdir -p /mnt/'+ start_time)
        print("\n Exporting Snapshot to backup directory /mnt/nas:" + hostname[i]+" - snapshot ID: "+snapid)
        exportsnap = sp.getoutput('xe snapshot-export-to-template snapshot-uuid=' + snapid+' filename=/mnt/'+start_time+'/'+hostname[i]+'-'+start_time+'.xva')
        logger.info(exportsnap)
        print("\n Export Snapshot completed for "+hostname[i])
        print("\n Removing Unnecassary Snapshot "+hostname[i])
        removesnap = sp.getoutput('xe snapshot-uninstall snapshot-uuid='+snapid+' --force')
        snap_remove = ("\n Looking for next VM to backup...")
        print(snap_remove)
        print(
            ".............................................................................")
        i = i+1
        logger.info(snap_remove)

    sp.getoutput('systemctl stop xenserverbkp.service')
    rm_old_dir = sp.getoutput('find /mnt/ -mtime +14 -type d')
    logger.info(rm_old_dir)
    sp.getouput('rm -rf rm_old_dir')

except IOError:
    print("\n Cannot continue further ERROR:Check your script!\n")
    error = ("\n Cannot continue further ERROR:Check your script!\n")
    logger.error(error)
