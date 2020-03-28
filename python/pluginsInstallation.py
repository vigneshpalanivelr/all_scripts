import os
import sys
import time
import urllib2
import argparse
import jenkinsapi
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.utils.crumb_requester import CrumbRequester

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

class installPlugins():
	def __init__(self, PublicIP, username, password):
		execLog.debug('Object  - Created Class Object')
		
		response	= urllib2.urlopen(PublicIP)
		JenkinsURL	= 'http://{}:8080'.format(response.read())
		execLog.debug('Jen URL - {}'.format(JenkinsURL))
		
		requester	= CrumbRequester(baseurl=JenkinsURL, username=username, password=password)
		self.server	 	= Jenkins(JenkinsURL, username=username, password=password, requester=requester)
		
		version 	= self.server.version
		execLog.info('Jenkins Server Version is : {}'.format(version))
		
		user 		= self.server.username
		execLog.info('Logged in to Jenkins as   : {}'.format(user))
	
	def install_plugins(self, pluginsList):
		index = 0
		for i in pluginsList:
			try:
				index = index + 1
				plugin = i + '@latest'
				self.server.install_plugin(plugin)
				execLog.info('Installed Plug-In : {} : {}'.format(index, i))
			except Exception as Error:
				execLog.error('Plugi-In Installation Error : '+Error.__class__.__name__ +' '+str(Error).rstrip())
	
	def list_plugins(self):
		index = 0
		for plugins in self.server.get_plugins().values():
			index = index + 1
			execLog.info('Availab Jenkins PlugIn : {} : {}'.format(index,plugins.shortName))

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Read ansible variables in YAML format')
	
	parser.add_argument('YAMLvarFile'	,action='store_const'	,help='Load Variables from Ansible Vars',const='../ansible/vars/vars.yml'						)
	parser.add_argument('-install'		,action='store_true'	,help='Set to switch to true'			,dest='install'						,default=False		)
	parser.add_argument('-list'			,action='store_true'	,help='Set to switch to true'			,dest='list'						,default=False		)
	
	# arguments			= parser.parse_args(['-install','-list'])
	arguments			= parser.parse_args()
	YAMLvarFile			= arguments.YAMLvarFile
	install				= arguments.install
	list				= arguments.list
	
	# Load variables from ansible vars
	variables 		= global_vars.get_ansible_vars(YAMLvarFile)
	logDirectory 	= variables['scriptHomeDir']+'/'+variables['scriptsDir']+'/'+variables['logsDir']
	
	# Execute a class object to make log dir
	loadLogDirectory()
	print 'Created Log Directory : {}'.format(logDirectory)
	
	# Define logging module, File Handler & Stream Handler
	# Define Log file name for later use
	execLogger		= 'jen-plugin-inst-log' + time.strftime('-%Y-%m-%d-%Hh-%Mm-%Ss-%Z') + '.log'
	execLog			= logger.setupLogger('YUM INstalation Steps', logDirectory +'/'+ execLogger)
	execLog.debug('Object  - Successfully Loadded Ansible Vars')
	
	# Creating class object
	install_plugins = installPlugins(
		variables['myPublicIP'],
		variables['repositories']['jenkins']['user'],
		variables['repositories']['jenkins']['password'],
		)
	
	# Execution
	if install:
		install_plugins.install_plugins(variables['repositories']['jenkins']['plugins'])
	if list:
		install_plugins.list_plugins()

# Ref : https://github.com/pycontribs/jenkinsapi/blob/master/jenkinsapi/jenkins.py
