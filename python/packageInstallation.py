#!/bin/python2
import os
import sys
import yum
import json
import time
import logger
import argparse
import prettytable

#import custom modules
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv'))
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/pySetenv/variables')
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/pySetenv/packages')
print sys.path

class packageInstalation(object):
	def __init__(self):
		# YumBase instance is the base class that houses methods and objects required to perform all the package management functions using yum.
		# For more : http://yum.baseurl.org/download/docs/yum-api/3.2.27/yum.YumBase-class.html#_delRepos
		try:
			self.yBase 						= yum.YumBase()
			self.yBase.preconf.debuglevel 	= 0
			self.yBase.preconf.errorlevel	= 0
			execLog.info('YUM Base SetUP  : {}'.format('YUM Base SetUp Completed'))
		except Exception as YumBaseError:
			execLog.error(str(YumBaseError).rstrip())
			exit(100)
	
	def CleanUp(self):
		# YumBase instance is the base class that houses methods and objects required to perform all the package management functions using yum.
		# For more : http://yum.baseurl.org/download/docs/yum-api/3.2.27/yum.YumBase-class.html#_delRepos
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
			execLog.info('Generated Pakgs : {}'.format('PrettyTable'))
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
		try:
			for pkg,ver in pkg2Install.iteritems():
				if not ver: 
					ver = None
					install		= self.yBase.install(name=pkg, version=ver)
					resolveDep	= self.yBase.resolveDeps()
					self.yBase.buildTransaction()
					if install:
						execLog.info('YUM Package Name : {} \tVersion : {} \tState : {}'.format(install[0].name, install[0].version, 'Installing...'))
					else:
						execLog.info('YUM Package Name : {} \tVersion : {} \tState : {}'.format(pkg, self.pkgCache[pkg]['version'],'AlreadyInstalled...!'))
				elif self.pkgCache.has_key(pkg):
					if self.pkgCache[pkg]['version'] == ver:
						execLog.info('YUM Package Name : {} \tVersion : {} \tState : {}'.format(pkg, self.pkgCache[pkg]['version'],'AlreadyInstalled...!'))
				else:
					install		= self.yBase.install(name=pkg, version=ver)
					resolveDep	= self.yBase.resolveDeps()
					self.yBase.buildTransaction()
					if install:
						execLog.info('YUM Package Name : {} \tVersion : {} \tState : {}'.format(install[0].name, install[0].version, 'Installing...'))
			# Real Installation Takes Place
			self.yBase.processTransaction()
			return True
		except Exception as pkgInstallationError:
			execLog.error(str(pkgInstallationError).rstrip())
			exit(500)

if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Script to Install Packages using Python YUM Module')
	
	parser.add_argument('packageDict'		,action='store'		,type=json.loads	,help='Packages dict to install')
	
	# Have to provide packageDict in below mentioned str format '""'
	# arguments	= parser.parse_args(['{"wget":"1.14","tree":"1.6.0","telnet":"0.17","git":""}'])
	arguments	= parser.parse_args()
	packageDict		= arguments.packageDict
	
	# Define Log file names
	execLogger			= 'packageExectnLog' + time.strftime('-%Y-%m-%d-%Hh-%Mm-%Ss-%Z') + '.log'
	
	# Define logging File & Stream Handlers
	execLog				= logger.setupLogger('Execution Step' ,execLogger)
	
	# Creating Class Object
	pkgInstalled 		= packageInstalation()
	
	# Execution
	try:
		if pkgInstalled.installedPackagesInServer():
			if pkgInstalled.installPakgs(packageDict):
				print '\n+---------------------------------------------------+---Completed---+------------------------+----------------+\n'
	except Exception as installedPackagesInServerError:
		execLog.error(str(installedPackagesInServerError).rstrip())
		exit(1)
