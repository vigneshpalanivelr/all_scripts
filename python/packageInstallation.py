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
		# Ref      : https://linuxhint.com/yum_centos_python/
		execLog.debug('Object  - Created Class Object : {}')
		try:
			self.yBase 						= yum.YumBase()
			self.yBase.preconf.debuglevel 	= 0
			self.yBase.preconf.errorlevel	= 0
			execLog.info('YUM Base SetUP  : {}'.format('YUM Base SetUp Completed'))
		except Exception as YumBaseError:
			execLog.error('Yum Base Object : '+YumBaseError.__class__.__name__ + ' ' + str(YumBaseError).rstrip())
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
			execLog.error('Yum Base CleanUp : '+YumBaseError.__class__.__name__ + ' ' + str(YumBaseError).rstrip())
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
			execLog.error('Generate Pretty Table : '+generatePrettyTablesError.__class__.__name__ + ' ' + str(generatePrettyTablesError).rstrip())
			exit(300)
	
	def installedPackagesInServer(self):
		try:
			execLog.info('YUM CleanUp     : In Progress...')
			self.CleanUp()
			fieldNames			= ["NAME", "VERSION", "RELEASE", "ARCHETECTURE"]
			
			self.packages		= self.yBase.doPackageLists()
			self.pkgCache		= {i.Name: {'version' : i.version} for i in sorted(self.packages['installed'])}
			pkgDetails			= [[i.Name ,i.version ,i.release ,i.arch] for i in sorted(self.packages['installed'])]
			
			print '\n' + str(self.generatePrettyTables(pkgDetails ,fieldNames)) + '\n'
			execLog.info('YUM CleanUp     : Completed')
			return True
		except Exception as PrettyTableCallInstalled:
			execLog.error('Pretty Table : '+PrettyTableCallInstalled.__class__.__name__ + ' ' + str(PrettyTableCallInstalled).rstrip())
			exit(400)
	
	def pkgCheck(self, pkg2Install):
		if type(pkg2Install) is dict:
			self.installPakgsDict(pkg2Install)
		elif type(pkg2Install) is str:
			self.installation(pkg2Install)
		else:
			raise ValueError('Accepts only Dict or Str values')
	
	def installPakgsDict(self, pkg2Install):
		for key,value in pkg2Install.iteritems():
			self.installation(value['name'], version=value['version'])
	
	def installation(self, package, version=None):
		try:
			start		= False
			install		= self.yBase.install(name=package, version=version)
			resolveDep	= self.yBase.resolveDeps()
			self.yBase.buildTransaction()
			if install:
				execLog.info('YUM Package Name : {} \tVersion : {} \tState : {}'.format(install[0].name, install[0].version, 'Installing...'))
			else:
				execLog.warning('YUM Package Name : {} \tVersion : {} \tState : {}'.format(package, self.pkgCache[package]['version'],'AlreadyInstalled...!'))
			start = True
		except yum.Errors.InstallError as InstallationError:
			execLog.error(InstallationError.__class__.__name__ +' '+str(InstallationError).rstrip()+' '+ package+' v'+str(version))
		if start is True:
			try:
				# Auto approval and Real Installation Takes Place
				self.yBase.conf.assumeyes = True
				self.yBase.processTransaction()
				if install:
					execLog.info('YUM Package Name : {} \tVersion : {} \tState : {}'.format(install[0].name, install[0].version, 'Completed'))
				self.yBase.closeRpmDB()
			except Exception as Error:
				execLog.error('Process Transaction : '+Error.__class__.__name__ +' '+str(Error).rstrip())
				exit(500)

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Read ansible variables in YAML format')
	
	parser.add_argument('YAMLvarFile'	,action='store_const'	,help='Load Variables from Ansible Vars',const='../ansible/vars/vars.yml'						)
	parser.add_argument('-t'			,action='store_true'	,help='Set to switch to true'			,dest='custome_install'				,default=False		)
	parser.add_argument('-a'			,action='append'		,help='Add list ofpkgs'					,dest='custome_packages'			,default=[]			)
	
	# arguments			= parser.parse_args(['../ansible/vars/vars.yml','-t','-a','ansible','-a','jenkins'])
	arguments			= parser.parse_args()
	YAMLvarFile			= arguments.YAMLvarFile
	custome_install		= arguments.custome_install
	custome_packages	= arguments.custome_packages
	
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
	if pkgInstalled.installedPackagesInServer():
		pkgInstalled.pkgCheck(variables['common_pks'])
		if custome_install:
			for i in custome_packages:
				pkgInstalled.pkgCheck(i)
