#!/bin/python2
import os
import sys
import yum
import yaml
import json
import time
import argparse
import prettytable

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

class packageInstalation(object):
	def __init__(self):
		# YumBase instance is the base class that houses methods and objects required to perform all the package management functions using yum.
		# For more : http://yum.baseurl.org/download/docs/yum-api/3.2.27/yum.YumBase-class.html#_delRepos
		execLog.debug('Object  - Created Class Object : {}')
		try:
			self.yBase 						= yum.YumBase()
			self.yBase.preconf.debuglevel 	= 0
			self.yBase.preconf.errorlevel	= 0
			execLog.info('YUM Base SetUP  : {}'.format('YUM Base SetUp Completed'))
		except Exception as YumBaseError:
			execLog.error(str(YumBaseError).rstrip())
			exit(100)
	
	def CleanUp(self):
		try:
			execLog.info('YUM Config File : {}'.format(self.yBase.conf.config_file_path))
			execLog.info('YUM Log File    : {}'.format(self.yBase.conf.logfile))
			execLog.info('YUM Error Level : {}'.format(self.yBase.conf.errorlevel))
			execLog.info('YUM CleanUp RPM : {}'.format(self.yBase.cleanRpmDB()[1][0]))
			execLog.info('YUM Exp Chache  : {}'.format(self.yBase.cleanExpireCache()[1][0]))
			execLog.info('YUM CleanUp MD  : {}'.format(self.yBase.cleanMetadata()[1][0]))
			execLog.info('YUM CleanUP SQL : {}'.format(self.yBase.cleanSqlite()[1][0]))
			execLog.info('YUM CleanUP PKG : {}'.format(self.yBase.cleanPackages()[1][0]))
			execLog.info('YUM ChacheSetUp : {}'.format(self.yBase.setCacheDir(force=True)))
		except Exception as YumBaseError:
			execLog.error(str(YumBaseError).rstrip())
			exit(200)
	
	def generatePrettyTables(self, nestedLists,fieldNames):
		PrettyTable 			= prettytable.PrettyTable()
		PrettyTable.field_names = fieldNames
		try:
			for i in nestedLists:
				PrettyTable.add_row(i)
			PrettyTable.align="l"
			PrettyTable.padding_width=2
			execLog.info('Generated Pakgs : PrettyTable')
			return PrettyTable
		except Exception as generatePrettyTablesError:
			execLog.error(str(generatePrettyTablesError).rstrip())
			exit(300)
	
	def installedPackagesInServer(self):
		try:
			execLog.info('YUM CleanUp     : In Progress...')
			self.CleanUp()
			# self.pkgDetails 	= []
			fieldNames			= ["NAME", "VERSION", "RELEASE", "ARCHETECTURE"]
			
			self.packages		= self.yBase.doPackageLists()
			self.pkgCache		= {i.Name: {'version' : i.version} for i in sorted(self.packages['installed'])}
			pkgDetails			= [[i.Name ,i.version ,i.release ,i.arch] for i in sorted(self.packages['installed'])]
			
			print '\n' + str(self.generatePrettyTables(pkgDetails ,fieldNames)) + '\n'
			execLog.info('YUM CleanUp     : Completed')
			
			return True
		except Exception as PrettyTableCallInstalled:
			execLog.error(str(PrettyTableCallInstalled).rstrip())
			exit(400)
	
	def installPakgs(self, pkg2Install):
		print pkg2Install
		try:
			for key,value in pkg2Install.iteritems():
				try: 
					install		= self.yBase.install(name=value['name'], version=value['version'])
					resolveDep	= self.yBase.resolveDeps()
					self.yBase.buildTransaction()
					if install:
						execLog.info('YUM Package Name : {} \tVersion : {} \tState : {}'.format(install[0].name, install[0].version, 'Installing...'))
					else:
						execLog.warning('YUM Package Name : {} \tVersion : {} \tState : {}'.format(value['name'], self.pkgCache[value['name']]['version'],'AlreadyInstalled...!'))
				except yum.Errors.InstallError as pkgInstallationError:
					execLog.error(str(pkgInstallationError).rstrip() + ' ' + value['name'] + ' ' +str(value['version']) + pkgInstallationError.__class__.__name__)
			# Real Installation Takes Place
			self.yBase.processTransaction()
			return True
		except Exception as pkgInstallationError:
			execLog.error(str(pkgInstallationError).rstrip())
			exit(500)

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Read ansible variables in YAML format')
	
	parser.add_argument('YAMLvarFile'               ,action='store_const'           ,help='Load Variables from Ansible Vars'        ,const='../ansible/vars/vars.yml' )
	
	# arguments		= parser.parse_args(['../ansible/vars/vars.yml'])
	arguments		= parser.parse_args()
	YAMLvarFile		= arguments.YAMLvarFile
	
	# Load variables from ansible vars
	variables 		= global_vars.get_ansible_vars(YAMLvarFile)
	logDirectory 	= variables['scriptHomeDir']+'/'+variables['scriptsDir']+'/'+variables['logsDir']
	
	# Execute a class object to make log dir
	loadLogDirectory()
	print 'Created Log Directory : {}'.format(logDirectory)
	
	# Define logging module, File Handler & Stream Handler
	# Define Log file name for later use
	execLogger		= 'packageExectnLog' + time.strftime('-%Y-%m-%d-%Hh-%Mm-%Ss-%Z') + '.log'
	execLog			= logger.setupLogger('YUM INstalation Steps', logDirectory +'/'+ execLogger)
	execLog.debug('Object  - Successfully Loadded Ansible Vars')
	
	# Creating class object
	pkgInstalled 	= packageInstalation()
	
	# Execution
	try:
		if pkgInstalled.installedPackagesInServer():
			pkgInstalled.installPakgs(variables['common_pks'])
	except Exception as installedPackages:
		execLog.error( installedPackages.__class__.__name__ + str(installedPackages).rstrip())
		exit(1)

