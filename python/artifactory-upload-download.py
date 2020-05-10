#!/bin/python2
# Ref : https://gist.github.com/junhe/806c57ce629e1d7035a1
# Ref : https://jsonlint.com/

import os
import sys
import json
import yaml
import shutil
import urllib2
import hashlib
import platform
import requests
import argparse
import datetime
from contextlib import closing

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
	def __init__(self, logDirectory):
		if not os.path.exists(logDirectory): os.makedirs(logDirectory)

class UploadDownload():
	def __init__(self, rti_ip_add, rti_port, rpm_local):
		self.pkg_metadata_url	= 'http://{}:{}/artifactory/{}/package-list/'.format(rti_ip_add, rti_port, rpm_local)
	
	def get_data(self, package_list):
		r = requests.get(self.pkg_metadata_url + package_list)
		if r.status_code == 200:
			with open(package_list, 'wb') as local_file:
				local_file.write(r.content)
			with open(package_list, 'r') as local_data:
				try:
					return yaml.safe_load(local_data)
				except yaml.YAMLError as exc:
					print exc
					return 0			
	
	def read_remote_json(self, git_acct, repo_name, file_path, commit, token, target_file=None):
		# token = os.getenv("GITHUB_TOKEN")
		# curl -H 'Authorization: token 90c044c690bc2b5e2efa3287a26d8464e86833c3' -H 'Accept: application/vnd.github.v3.raw' -L https://raw.githubusercontent.com/vigneshpalanivelr/all_scripts/c1732f1a64bf6239837f1fa106f43837c6256d3e/artifactory/package_list.json
		
		url 	= 'https://raw.githubusercontent.com/{git_acct}/{repo_name}/{commit}/{file_path}'.format(git_acct=git_acct, repo_name=repo_name, commit=commit, file_path=file_path)
		headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': 'token {}'.format(token), 'Accept': 'application/vnd.github.v3.raw'}
		
		if not token:
			raise RuntimeError("Please provide the token from GitHub -> Settings -> Developer settings -> Personal access tokens -> ReadToken")
		
		r = requests.get(url, headers=headers, stream=True)
		if r.status_code == 200:
			if target_file:
				with open(target_file,'w') as json_data:
					json.dump(r.content, json_data)
			return r.json()
	
	def yaml_setup_update(self, package_list, setup=False, os_versions_list=None):
		global data
		if setup:
			data = {'RHEL' : {i:{} for i in os_versions_list} }
		else:
			data = data
		with open(package_list, 'wb') as yaml_setup:
				yaml.safe_dump(data, yaml_setup)
		self.upload(self.pkg_metadata_url, package_list, rti_user, rti_pass)
		return data
	
	def rpm_check(self, element, postgres_rpm, jenkins_rpm, cw_rpm, epel_rpm):
		if 'PostgreSQL' in element['Description']:
			return postgres_rpm
		elif 'Jenkins' in element['Description']:
			return jenkins_rpm
		elif 'CloudWatch' in element['Description']:
			return cw_rpm
		elif 'EPEL' in element['Description']:
			return epel_rpm
	
	def download_check(self, element, version, rpm_dir):
		global data
		try: 
			packages = [i['package'] for i in data['RHEL'][version][rpm_dir]]
			if element['package'] in packages:
				if i['status'] == 'Uploaded':
					return False, 'Already-Uploaded'
				if i['status'] == 'Failed':
					return True, 'Re-Upload'
			elif element['package'] not in packages:
				return True, 'Fresh-Upload'
		except KeyError as Error:
			data['RHEL'][version][rpm_dir] = []
			return True, 'Fresh-Upload'
	
	def get_md5(self, file):
		md5 = hashlib.md5()
		with open(file, 'rb') as f:
			for chunk in f:
				md5.update(chunk)
		return md5.hexdigest()
	
	def get_sha1(self, file):
		sha1 = hashlib.sha1()
		with open(file, 'rb') as f:
			for chunk in f:
				sha1.update(chunk)
		return sha1.hexdigest()
	
	def upload(self, artifactory_url, file, rti_user, rti_pass):
		base_file_name 	= os.path.basename(file)
		md5hash 		= self.get_md5(file)
		sha1hash 		= self.get_sha1(file)
		headers 		= {"X-Checksum-Md5": md5hash, "X-Checksum-Sha1": sha1hash}
		print 
		print 'Uploading RPM          : {}'.format(base_file_name)
		print 'Artifactory Target Dir : {}{}'.format(artifactory_url, base_file_name)
		r 				= requests.put("{}{}".format(artifactory_url, base_file_name), auth=(rti_user, rti_pass), headers=headers, verify=False, data=open(file, 'rb'))
		return r.status_code
	
	def download_upload(self, element, package_list, rpm_target_dir, artifactory_url, rti_user, rti_pass, os_versions_list, postgres_rpm, jenkins_rpm, cw_rpm, epel_rpm):
		global data
		if element['osVersion'] == 'any':
			versions = os_versions_list
		else:
			versions = str(element['osVersion']).split(',')
		for version in versions:
			rpm_dir				= self.rpm_check(element, postgres_rpm, jenkins_rpm, cw_rpm, epel_rpm)
			status, upload_type = self.download_check(element, version, rpm_dir)
			if status:
				print '*********************************************************************'
				print #str(datetime.datetime.now())
				print json.dumps(element, sort_keys=True, indent=4, separators=(',', ' : '))
				print
				timeStart = datetime.datetime.now()
				print 'Start Time             : ' + str(timeStart)
				print 'Downloading RPM File   : {}'.format(element['package'])
				
				if element['downloadURL'].split(':')[0] in 'https':
					rs	= requests.Session()
					r	= requests.get(element['downloadURL'] + element['package'], stream=True)
					print 'Download Response Code : {}'.format(r.status_code)
					
					if r.status_code == 200 and not os.path.exists(rpm_target_dir + element['package']):
						with open(rpm_target_dir + element['package'], 'wb') as rpm:
							for chunk in r.iter_content(chunk_size=1024):
								if chunk:
									rpm.write(chunk)
						print 'Download Completed'
				elif element['downloadURL'].split(':')[0] in 'ftp' and not os.path.exists(rpm_target_dir + element['package']):
					with closing(urllib2.urlopen(element['downloadURL'] + element['package'])) as r:
						with open(rpm_target_dir + element['package'], 'wb') as f:
							shutil.copyfileobj(r, f)
					print 'Download Completed'
				
				timeCompleted = datetime.datetime.now()
				print 'Download Elapsed Time  : {}'.format(timeCompleted - timeStart)
				print '*********************************************************************'
				
				try:
					status_code = self.upload(artifactory_url + version + '/' + rpm_dir + '/packages/', rpm_target_dir + element['package'], rti_user, rti_pass)
					print 'Upload Response Code   : {}'.format(status_code)
					if upload_type == 'Fresh-Upload' and status_code == 201:
						data['RHEL'][version][rpm_dir].append({'package' : element['package'], 'status' : 'Failed', 'Date' : element['releaseDate']})
					elif upload_type == 'Re-Upload' and status_code == 201:
						for i in data['RHEL'][version][rpm_dir]:
							if element['package'] == i['package']:
								i['status'] = 'Uploaded'
					elif upload_type == 'Re-Upload' and status_code != 201:
						for i in data['RHEL'][version][rpm_dir]:
							if element['package'] == i['package']:
								i['status'] = 'Failed'
					elif upload_type == 'Fresh-Upload' and status_code != 201:
						data['RHEL'][version][rpm_dir].append({'package' : element['package'], 'status' : 'Failed', 'Date' : element['releaseDate']})
					self.yaml_setup_update(package_list, setup=False)
				except UnboundLocalError as Error:
					pass
			else:
				print '*********************************************************************'
				print 
				print 'RPM is Already Uploaded: {}'.format(artifactory_url + version + '/' + rpm_dir + '/packages/' + element['package'])

if __name__ == '__main__':
	
	# Argparse Argments and variables defination
	parser = argparse.ArgumentParser(description='Artifactory Upload-Download Scripts')
	
	try : 
		parser.add_argument('YAMLvarFile'	,action='store_const'	,help='Variables from Ansible Vars'	,const='../ansible/vars/vars.yml'		)
		parser.add_argument('package_list'	,action='store_const'	,help='Package List YAML file'		,const='package_list.yaml'				)
		
		parser.add_argument('git_acct'		,action='store_const'	,help='GitHub Account'				,const='vigneshpalanivelr'				)
		parser.add_argument('repo_name'		,action='store_const'	,help='Repository Name'				,const='all_scripts'					)
		parser.add_argument('commit'		,action='store'			,help='Full Commit SHA-ID'													)
		parser.add_argument('file_path'		,action='store_const'	,help='Repo File Path to read'		,const='artifactory/package_list.json'	)
		parser.add_argument('token'			,action='store'			,help='GitHub -> Settings -> Developer settings -> Personal access tokens -> ReadToken')
		parser.add_argument('-target_file'	,action='store'			,help='File to store output'		,dest='target_file'						)
		
		parser.add_argument('-rti_user'		,action='store'			,help='Artifactory Account User'	,dest='rti_user'						)
		parser.add_argument('-rti_pass'		,action='store'			,help='Artifactory Account Pass'	,dest='rti_pass'						)
		parser.add_argument('-rti_ip_add'	,action='store'			,help='Artifactory IP Address'		,dest='rti_ip_add'						)
		parser.add_argument('rti_port'		,action='store_const'	,help='Artifactory Port'			,const='8081'							)
		
		parser.add_argument('rpm_local'		,action='store_const'	,help='Artifactory Local RPM'		,const='rpm-local'						)
		parser.add_argument('postgres_rpm'	,action='store_const'	,help='PostgreSQL Path'				,const='postgres-rpm'					)
		parser.add_argument('jenkins_rpm'	,action='store_const'	,help='Jenkins Path'				,const='jenkins-rpm'					)
		parser.add_argument('cw_rpm'		,action='store_const'	,help='CloudWatch Path'				,const='cw-rpm'							)
		parser.add_argument('epel_rpm'		,action='store_const'	,help='EPEL Path'					,const='epel-rpm'						)
		
		# argdic	= vars(arguments)
		# arguments = parser.parse_args()
		arguments			= parser.parse_args([
							'be43981eb60e611bfb377bdea7b021dc3b2d9d11',
							'90c044c690bc2b5e2efa3287a26d8464e86833c3',
							'-rti_ip_add',
							'172.31.46.139',
							'-rti_user',
							'admin',
							'-rti_pass',
							'admin'
							])
		
	except:
		parser.print_help()
		exit(1)
	
	YAMLvarFile			= arguments.YAMLvarFile
	package_list		= arguments.package_list
	
	git_acct			= arguments.git_acct
	repo_name			= arguments.repo_name
	commit				= arguments.commit
	file_path			= arguments.file_path
	token				= arguments.token
	target_file			= arguments.target_file
	
	rti_user			= arguments.rti_user
	rti_pass			= arguments.rti_pass
	rti_ip_add			= arguments.rti_ip_add
	rti_port			= arguments.rti_port
	
	rpm_local			= arguments.rpm_local
	postgres_rpm		= arguments.postgres_rpm
	jenkins_rpm			= arguments.jenkins_rpm
	cw_rpm				= arguments.cw_rpm
	epel_rpm			= arguments.epel_rpm
	
	artifactory_url		= 'http://{}:{}/artifactory/{}/RHEL/'.format(rti_ip_add, rti_port, rpm_local)
	os_versions_list	= ['6','7','8']
	download_target		= '/downloaded_rpm/'
	rpm_target_dir		= os.getcwd() + download_target
	
	
	# Load variables from ansible vars
	variables 		= global_vars.get_ansible_vars(YAMLvarFile)
	logDirectory 	= variables['scriptHomeDir']+'/'+variables['scriptsDir']+'/'+variables['logsDir']
	
	# Execute a class object to make log dir
	loadLogDirectory()
	print 'Created Log Directory : {}'.format(logDirectory)
	
	# Execute a class object to make log dir
	loadLogDirectory(os.getcwd() + download_target)
	
	# Define logging module, File Handler & Stream Handler
	# Define Log file name for later use
	execLogger		= 'rti-upload-download' + time.strftime('-%Y-%m-%d-%Hh-%Mm-%Ss-%Z') + '.log'
	execLog			= logger.setupLogger('Artifactory Upload-Download', logDirectory +'/'+ execLogger)
	execLog.debug('Object  - Successfully Loadded Ansible Vars')
	
	# Creating class object
	upload_download 	= UploadDownload(rti_ip_add, rti_port, rpm_local)
	
	# Local YAML Read
	data = upload_download.get_data(package_list)
	# data = upload_download.parse_yaml()
	if not data:
		data = upload_download.yaml_setup_update(package_list, setup=True, os_versions_list=os_versions_list)
	
	# Remote JSON Read
	remote_json = upload_download.read_remote_json(git_acct, repo_name, file_path, commit, token, target_file)
	for date in sorted(set([i['releaseDate'] for i in remote_json])):
		for remote_element in remote_json:
			if date == remote_element['releaseDate']:
				upload_download.download_upload(remote_element, package_list, rpm_target_dir, artifactory_url, rti_user, rti_pass, os_versions_list ,postgres_rpm, jenkins_rpm, cw_rpm, epel_rpm)