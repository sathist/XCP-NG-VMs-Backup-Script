# XCP-NG-VMs-Backup-Script
1. All VM’s and data are taken backup using Python and Shell scripts
2. Scripts are added in the system service file

# For service log store - Backup VM's name.
4. sudo mkdir /var/log/xenserverbkp

# Add service file in this file path
# Add cron jobs to run the script
6. Add service to /etc/systemd/system/multi-user.target.wants/
7.    sudo systemctl xenserverbkp start
8.    sudo systemctl xenserverbkp status
9.    sudo systemctl enable xenserverbkp
