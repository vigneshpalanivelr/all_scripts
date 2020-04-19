#/bin/bash

device=$1
mount=$2

#Creating a temporary Directory and mount 
mkdir /backup
mount ${device} /backup

#Copy all the data to backup device
rsync -a ${mount}/* /backup

#Un-Mount the backup and mount device
umount ${device}
mount ${device} ${mount}

#Remove the backup
rm -rf /backup
restorecon -R ${mount}