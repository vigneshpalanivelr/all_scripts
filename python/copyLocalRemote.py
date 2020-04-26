#!/bin/python2
import os
import sys
# import yum
# import glob
import yaml
import json
import time
import stat
import shutil
import fnmatch
import argparse
import requests
import fileinput
import subprocess
# import prettytable

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

class CopyExtract(object):
	def __init__(self):
		execLog.debug('Object  - Created Class Object')
		pass
	
	def copy_remote(self, allDirs=None, source='../', destination=None):
		execLog.debug('Action  - Started coping to Remote path')
		for i in allDirs:
			self.copytree(source+i, destination+i)
		execLog.debug('Done    - Completed coping to Remote path')
	
	def copy_destination(self, allDirs=None, source=None, yumDir=None, initDir=None, systmdDir=None, RHEL=None, repos=None):
		execLog.debug('Action  - Started coping to Destination path')
		for i in allDirs:
			if 'repo' in i:
				execLog.debug('Action  - Found Repo files')
				for basename, filename in self.find_files(source+i, '*repo*'):
					self.copytree(filename , yumDir, permission = variables['yumDirPer'])
					if 'epel' in basename and 'epel' in repos:
						self.find_replace(yumDir+'/'+basename, 'OS_VERSION', RHEL)
						self.get_GPG_KEY(
							variables['repositories']['epel']['repo']+variables['repositories']['epel']['gpgurl']+RHEL,
							variables['GPG_KEY_Dir']+variables['repositories']['epel']['gpgkey']+RHEL
						)
					if 'jenkins' in basename and 'jenkins' in repos:
						self.find_replace(yumDir+'/'+basename, 'JENKINS_REPO', variables['repositories']['jenkins']['repo'])
						self.find_replace(yumDir+'/'+basename, 'JENKINS_GPGKEY', variables['repositories']['jenkins']['gpgkey'])
						self.get_GPG_KEY(
							variables['repositories']['jenkins']['repo']+variables['repositories']['jenkins']['gpgurl'],
							variables['GPG_KEY_Dir']+variables['repositories']['jenkins']['gpgkey']
						)
					if 'artifactory' in basename and 'artifactory' in repos:
						self.find_replace(yumDir+'/'+basename, 'ARTIFACTORY_REPO', variables['repositories']['artifactory']['repo'])
					if 'jfrog-cw' in basename and 'jfrog-cw' in repos:
						self.find_replace(yumDir+'/'+basename, 'CW_LOCAL_REPO', variables['repositories']['jfrog-cw']['repo'])
						self.find_replace(yumDir+'/'+basename, 'OS_VERSION', RHEL)
					if 'jfrog-epel' in basename and 'jfrog-epel' in repos:
						self.find_replace(yumDir+'/'+basename, 'EPEL_LOCAL_REPO', variables['repositories']['jfrog-epel']['repo'])
						self.find_replace(yumDir+'/'+basename, 'OS_VERSION', RHEL)
					if 'jfrog-jenkins' in basename and 'jfrog-jenkins' in repos:
						self.find_replace(yumDir+'/'+basename, 'JENKINS_LOCAL_REPO', variables['repositories']['jfrog-jenkins']['repo'])
						self.find_replace(yumDir+'/'+basename, 'OS_VERSION', RHEL)
					if 'jfrog-postgresql' in basename and 'jfrog-postgresql' in repos:
						self.find_replace(yumDir+'/'+basename, 'POSTGRESQL_LOCAL_REPO', variables['repositories']['jfrog-postgresql']['repo'])
						self.find_replace(yumDir+'/'+basename, 'OS_VERSION', RHEL)
			elif 'service' in i and RHEL == '6':
				execLog.debug('Action  - Found Service files for RHEL {}'.format(RHEL))
				for basename, filename in self.find_files(source+i, '*Initd*'):
					self.copytree(filename , initDir, permission = variables['initDirPer'])
			elif 'service' in i and RHEL == '7':
				execLog.debug('Action  - Found Service files for RHEL {}'.format(RHEL))
				for basename, filename in self.find_files(source+i, '*Initd*'):
					self.copytree(filename , initDir, permission = variables['initDirPer'])
			elif 'service' in i and RHEL == '8':
				execLog.debug('Action  - Found Service files for RHEL {}'.format(RHEL))
				for basename, filename in self.find_files(source+i, '*Services*'):
					self.copytree(filename , systmdDir, permission = variables['systemdDirPer'])
			elif 'python' in i:
				execLog.debug('Action  - Found Python files')
				for basename, filename in self.find_files(source+i, '*.py*'):
					self.permission_restore(filename, variables['pythonPer'],)
					execLog.info('Permisn  - {} : {} : {}'.format(source+i, filename, variables['pythonPer']))
		execLog.debug('Done    - Completed coping to Destination path')
	
	def copytree(self, src, dst, symlinks = False, ignore = None, permission = None):
		# Ref : https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
		if not os.path.exists(dst):
			os.makedirs(dst)
			shutil.copystat(src, dst)
			execLog.info('New File - {} : {}'.format(src, dst))
		if os.path.isdir(src):
			copy_list = os.listdir(src)
		elif os.path.isfile(src):
			copy_list = [src.split('/')[-1]]
			src       = '/'.join(src.split('/')[:-1])
		if ignore:
			exclude 	= ignore(src, copy_list)
			copy_list 	= [x for x in copy_list if x not in exclude]
			execLog.warning('Files Excluded List: {}'.format(exclude))
		for item in copy_list:
			s = os.path.join(src, item)
			d = os.path.join(dst, item)
			if symlinks and os.path.islink(s):
				if os.path.lexists(d):
					os.remove(d)
				os.symlink(os.readlink(s), d)
				try:
					st		= os.lstat(s)
					mode	= stat.S_IMODE(st.st_mode)
					os.lchmod(d, mode)
				except:
					pass # lchmod not available
			elif os.path.isdir(s):
				self.copytree(s, d, symlinks, ignore)
			else:
				shutil.copy2(s, d)
				if permission == None:
					execLog.info('Copying  - {} : {}'.format(s, d))
				elif permission != None:
					self.permission_restore(d , permission)
					execLog.info('Copying  - {} : {} : {}'.format(s, d, permission))
	
	def find_files(self, directory, regex):
		for root, dirs, files in os.walk(directory):
			for basename in files:
				if fnmatch.fnmatch(basename, regex):
					filename = os.path.join(root, basename)
					yield basename, filename
	
	def find_replace(self, filename, textToSearch, textToReplace):
		with open(filename,'r+') as file:
			filedata = file.read()
			filedata = filedata.replace(textToSearch, textToReplace)
			file.truncate(0)
			file.seek(0) 
			file.write(filedata)
		execLog.info('Find Re  - {} : {} : {}'.format(filename, textToSearch, textToReplace))
	
	def permission_restore(self, file, permission):
		subprocess.call(['chmod', permission, file])
	
	def get_GPG_KEY(self, url, key_file):
		with open(key_file, 'w') as gpg_file:
			gpg_file.write(requests.get(url).text)
		execLog.info('Set GPG  - {}'.format(key_file))

if __name__ == '__main__':
	
	# Argparse Argments and variables defination
	parser = argparse.ArgumentParser(description='Copy scripts from local to remote and enable services and repos')
	parser.add_argument('RHEL'			,action='store'			,help='RHEL Major Version'					,choices=['6','7','8']							)
	parser.add_argument('YAMLvarFile'	,action='store_const'	,help='Load Variables from Ansible Vars'	,const='../ansible/vars/vars.yml'				)
	parser.add_argument('-repos'		,action='append'		,help='Add list of repos to enable'			,dest='repos'						,default=[]	)
	
	# arguments		= parser.parse_args(['7','-repos','epel','-repos','jenkins','-repos','artifactory'])
	arguments		= parser.parse_args()
	RHEL			= arguments.RHEL
	YAMLvarFile		= arguments.YAMLvarFile
	repos			= arguments.repos
	
	# Load variables from ansible vars
	variables 		= global_vars.get_ansible_vars(YAMLvarFile)
	logDirectory 	= variables['scriptHomeDir']+'/'+variables['scriptsDir']+'/'+variables['logsDir']
	
	# Execute a class object to make log dir
	loadLogDirectory()
	print 'Created Log Directory : {}'.format(logDirectory)
	
	# Define logging module, File Handler & Stream Handler
	# Define Log file name for later use
	execLogger		= 'cp-local-remote-log' + time.strftime('-%Y-%m-%d-%Hh-%Mm-%Ss-%Z') + '.log'
	execLog			= logger.setupLogger('Copy Local to Remote', logDirectory +'/'+ execLogger)
	execLog.debug('Object  - Successfully Loadded Ansible Vars')
	
	# Creating class object
	copy_extract 	= CopyExtract()
	
	
	copy_extract.copy_remote(
		allDirs		= [variables['srcPythonDir'],variables['srcRepoDir'],variables['srcServicesDir']], 
		source 		= '../', 
		destination	= variables['scriptHomeDir']+'/'+variables['scriptsDir']+'/'
	)
	
	copy_extract.copy_destination(
		allDirs		= [variables['srcPythonDir'],variables['srcRepoDir'],variables['srcServicesDir']], 
		source 		= variables['scriptHomeDir']+'/'+variables['scriptsDir']+'/',
		yumDir		= variables['yumDir'],
		initDir		= variables['initDir'],
		systmdDir	= variables['systemdDir'],
		RHEL		= RHEL,
		repos		= repos
	)


