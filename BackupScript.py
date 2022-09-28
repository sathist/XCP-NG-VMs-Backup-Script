import subprocess as sp
import os
from datetime import datetime
import logging

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd

logging.basicConfig(filename="/var/log/xenserverbkp/xenserver-backuper.log", format='%(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

server_name = sp.getoutput('hostname')
from_id = 'From_ID'
mail_password = 'App_Paasword'
to_mail_id = 'To_ID','To_ID_2'

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
        sp.getoutput('mkdir -p /mnt/nas/'+ start_time)
        print("\n Exporting Snapshot to backup directory /mnt/nas:" + hostname[i]+" - snapshot ID: "+snapid)
        exportsnap = sp.getoutput('xe snapshot-export-to-template snapshot-uuid=' + snapid+' filename=/mnt/nas/'+start_time+'/'+hostname[i]+'-'+start_time+'.xva')
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
    rm_old_dir = sp.getoutput('find /mnt/nas/ -mtime +14 -type d')
    logger.info(rm_old_dir)
    sp.getouput('rm -rf rm_old_dir')

except IOError:
    print("\n Cannot continue further ERROR:Check your script!\n")
    error = ("\n Cannot continue further ERROR:Check your script!\n")
    logger.error(error)



    html = '''
        <html>
            <body>
                <h3>All VM's backups done - Success </h3>

            </body>
        </html>
        '''

    email_from = from_id
    password = mail_password
    email_to = to_mail_id
    serviceStatus = '\U0001f7e2' + server_name + ' Backup success ' 

except IOError:
    print("\n Cannot continue further ERROR:Check your script!\n")
    error = ("\n Cannot continue further ERROR:Check your script!\n")
    logger.error(error)

    html = '''
        <html>
            <body>
                <h3>Cannot continue further ERROR:Check your script &  VM's are NOT backedup </h3>
            </body>
        </html>
        '''

    email_from = from_id
    password = mail_password
    email_to = to_mail_id
    serviceStatus = '\U0001f534' + server_name + ' Backup failed '

# Mail config
try:
    # Generate today's date to be included in the email Subject
    date_str = pd.Timestamp.today().strftime('%Y-%m-%d')

    # Create a MIMEMultipart class, and set up the From, To, Subject fields
    email_message = MIMEMultipart()
    email_message['From'] = email_from
    email_message['To'] = ", ".join(email_to)
    email_message['Subject'] = f'{serviceStatus} - Mirrorfly Xenserver - {date_str} - Log'

    # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
    email_message.attach(MIMEText(html, "html"))

    # Convert it as a string
    email_string = email_message.as_string()
    
    # Connect to the Gmail SMTP server and Send Email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_from, password)
        server.sendmail(email_from, email_to, email_string)
except Exception as e: 
    print('Run time Error' + e)
