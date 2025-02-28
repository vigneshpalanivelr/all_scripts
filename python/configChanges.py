#!/bin/python2
import os
import sys
# import yaml
import json
import time
# import stat
# import shutil
import urllib2
import fnmatch
import requests
import argparse
# import requests
# import fileinput
import subprocess


#import custom modules
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv/variables'))
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv/packages'))
# sys.path.append(os.path.dirname('/root/all_scripts/python/pySetenv/variables/'))
# sys.path.append(os.path.dirname('/root/all_scripts/python/pySetenv/packages/'))
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
	
	def jenkins_url(self, PublicIP, pwdFile):
		response		= urllib2.urlopen(PublicIP)
		JenkinsURL		= 'http://{}:8080'.format(response.read())
		execLog.info('Jenk URL - {}'.format(JenkinsURL))
		self.jenkins_sign_up(JenkinsURL, pwdFile)
	
	def jenkins_sign_up(self, url, pwdFile):
		sec = 0
		while True:
			try:
				request_status = requests.get(url)
				if request_status.status_code == 403:
					execLog.info('   Jenkins is Up and Running after : {}secs'.format(sec))
					with open(pwdFile, 'r') as filedata:
						password = filedata.read()
						execLog.info('Jenk PWD - {}'.format(password))
					break
			except requests.exceptions.ConnectionError as Error:
				pass
			sec = sec + 5
			execLog.warning('Waiting for jenkins to come up  : {}secs'.format(sec))
			time.sleep(5)
	
	def configure_ansible(self, config_file):
		self.find_replace(config_file, '#host_key_checking = False', 'host_key_checking = False')
	
	def find_replace(self, filename, textToSearch, textToReplace):
		with open(filename,'r+') as file:
			filedata = file.read()
			filedata = filedata.replace(textToSearch, textToReplace)
			file.truncate(0)
			file.seek(0) 
			file.write(filedata)
		execLog.info('Find Re  - {} : {} : {}'.format(filename, textToSearch, textToReplace))
	
	def py_modules(self, modules):
		index = 0
		for module in modules:
			try:
				index = index + 1
				if subprocess.check_call([sys.executable, '-m', 'pip', 'install', module]) == 0:
					execLog.info('Installed Module  : {} : {}'.format(index, module))
			except subprocess.CalledProcessError as ModuleError:
				if subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', module]) == 0:
					execLog.info('Installed Module  : {} : {}'.format(index, module))
			except Exception as Error:
				execLog.error('Module Installation Error : '+ Error.__class__.__name__ +' '+str(Error).rstrip())

if __name__ == '__main__':
	
	# Argparse Argments and variables defination
	parser = argparse.ArgumentParser(description='Copy scripts from local to remote and enable services and repos')
	parser.add_argument('RHEL'			,action='store'			,help='RHEL Major Version'					,choices=['6','7','8']									)
	parser.add_argument('YAMLvarFile'	,action='store_const'	,help='Load Variables from Ansible Vars'	,const='../ansible/vars/vars.yml'						)
	parser.add_argument('-start'		,action='store_true'	,help='Set to switch to true'				,dest='start_services'				,default=False		)
	parser.add_argument('-service'		,action='append'		,help='Add list of pkgs'					,dest='services'					,default=[]			)
	parser.add_argument('-py_module'	,action='store_true'	,help='Set to switch to true'				,dest='py_module'					,default=False		)
	parser.add_argument('-ansible'		,action='store_true'	,help='Set to switch to true'				,dest='ansible'						,default=False		)
	
	# arguments		= parser.parse_args(['7', '-py_module' ,'-start', '-service', 'SSH', '-service','jenkins'])
	arguments		= parser.parse_args()
	RHEL			= arguments.RHEL
	YAMLvarFile		= arguments.YAMLvarFile
	start_services	= arguments.start_services
	services		= arguments.services
	py_module		= arguments.py_module
	ansible			= arguments.ansible
	
	# Load variables from ansible vars
	variables 		= global_vars.get_ansible_vars(YAMLvarFile)
	logDirectory 	= variables['scriptHomeDir']+'/'+variables['scriptsDir']+'/'+variables['logsDir']
	
	# Execute a class object to make log dir
	loadLogDirectory()
	print 'Created Log Directory : {}'.format(logDirectory)
	
	# Define logging module, File Handler & Stream Handler
	# Define Log file name for later use
	execLogger		= 'confgtn-changes-log' + time.strftime('-%Y-%m-%d-%Hh-%Mm-%Ss-%Z') + '.log'
	execLog			= logger.setupLogger('Service Restart', logDirectory +'/'+ execLogger)
	execLog.debug('Object  - Successfully Loadded Ansible Vars')
	
	# Creating class object
	enable_services 	= enableServices()
	
	for i in services:
		if start_services:
			enable_services.service_demon(
				initDir		= variables['initDir'],
				systmdDir	= variables['systemdDir'],
				RHEL		= RHEL,
				pattern		= i
			)
		if i == 'jenkins' :
			enable_services.jenkins_url(
				variables['myPublicIP'],
				variables['repositories']['jenkins']['pwd']
				)
	if py_module:
		enable_services.py_modules(variables['pyModules'])
	
	if ansible :
		enable_services.configure_ansible(
			variables['ansible']['conf_file']
			)
