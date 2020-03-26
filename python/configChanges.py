#!/bin/python2
import os
import sys
# import yaml
import json
import time
# import stat
# import shutil
import fnmatch
import argparse
# import requests
# import fileinput
import subprocess


#import custom modules
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv/variables'))
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv/packages'))
#sys.path.append(os.path.dirname('/root/all_scripts/python/pySetenv/variables/'))
#sys.path.append(os.path.dirname('/root/all_scripts/python/pySetenv/packages/'))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/pySetenv/variables/' )
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/pySetenv/packages/'  )
import logger
import global_vars
# print sys.path

class loadLogDirectory():
	def __init__(self):
		if not os.path.exists(logDirectory): os.makedirs(logDirectory)

class enableServices(object):
	def __init__(self):
		execLog.debug('Object  - Created Class Object')
		pass
	
	def service_demon(self, initDir=None, systmdDir=None, RHEL=None, pattern=None):
		try:
			for basename, filename in self.find_files(initDir, '*'+pattern+'*'):
				execLog.info('Service  - {}'.format(pattern))
				if RHEL == '6': self.command_exec([['/sbin/chkconfig', basename, 'on'],    ['/bin/systemctl', 'daemon-reload'], ['/bin/systemctl', 'restart', basename]])
				if RHEL == '7': self.command_exec([['/bin/systemctl', 'enable', basename], ['/bin/systemctl', 'daemon-reload'], ['/bin/systemctl', 'restart', basename]])
				if RHEL == '8': self.command_exec([['/bin/systemctl', 'enable', basename], ['/bin/systemctl', 'daemon-reload'], ['/bin/systemctl', 'restart', basename]])
				execLog.info('Service  - Completed service {}'.format(pattern))
		except Exception as serviceError:
			execLog.error(serviceError.__class__.__name__ + ' ' + str(serviceError).rstrip())
	
	def find_files(self, directory, regex):
		for root, dirs, files in os.walk(directory):
			for basename in files:
				if fnmatch.fnmatch(basename, regex):
					filename = os.path.join(root, basename)
					yield basename, filename
	
	def command_exec(self, commands):
		for i in commands:
			process 		= subprocess.Popen(i, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr 	= process.communicate()
			if 'Executing /sbin/chkconfig' in stderr:
				execLog.info('Command  - {}'.format(' '.join(i)))
			elif stderr:
				execLog.error('Command  - {}'.format(' '.join(i)))
			else:
				execLog.info('Command  - {}'.format(' '.join(i)))

if __name__ == '__main__':
	
	# Argparse Argments and variables defination
	parser = argparse.ArgumentParser(description='Copy scripts from local to remote and enable services and repos')
	parser.add_argument('RHEL'			,action='store'			,help='RHEL Major Version'					,choices=['6','7','8']									)
	parser.add_argument('YAMLvarFile'	,action='store_const'	,help='Load Variables from Ansible Vars'	,const='../ansible/vars/vars.yml'						)
	parser.add_argument('-t'			,action='store_true'	,help='Set to switch to true'				,dest='seart_services'				,default=False		)
	parser.add_argument('-a'			,action='append'		,help='Add list of pkgs'					,dest='services'					,default=[]			)
	
	# arguments		= parser.parse_args(['7', '-t', '-a', 'SSH', '-a','jenkins'])
	arguments		= parser.parse_args()
	RHEL			= arguments.RHEL
	YAMLvarFile		= arguments.YAMLvarFile
	seart_services	= arguments.seart_services
	services		= arguments.services
	
	# Load variables from ansible vars
	variables 		= global_vars.get_ansible_vars(YAMLvarFile)
	logDirectory 	= variables['scriptHomeDir']+'/'+variables['scriptsDir']+'/'+variables['logsDir']
	
	# Execute a class object to make log dir
	loadLogDirectory()
	print 'Created Log Directory : {}'.format(logDirectory)
	
	# Define logging module, File Handler & Stream Handler
	# Define Log file name for later use
	execLogger		= 'enable_services' + time.strftime('-%Y-%m-%d-%Hh-%Mm-%Ss-%Z') + '.log'
	execLog			= logger.setupLogger('Service Restart', logDirectory +'/'+ execLogger)
	execLog.debug('Object  - Successfully Loadded Ansible Vars')
	
	# Creating class object
	enable_services 	= enableServices()
	
	if seart_services:
		for i in services:
			if i:
				enable_services.service_demon(
					initDir		= variables['initDir'],
					systmdDir	= variables['systemdDir'],
					RHEL		= RHEL,
					pattern		= i
				)
