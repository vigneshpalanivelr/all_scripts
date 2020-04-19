#!/bin/python2
'''
Python script to Support YUM Operations

Required system related modules  : yum, rpm, rpmUtils
Required module for JSON obj     : json
Required module for system info  : os, sys, time, platform, inspect
Required module for cmd line arg : argparse
Custome Modules                  : logger, global_vars

References
https://raw.githubusercontent.com/studer/salt/master/salt/modules/yumpkg.py
yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm -y
'''
from __future__ import division
import os
import sys
import yum
import rpm
import json
import time
import inspect
import platform
import argparse
from rpmUtils.arch import getBaseArch	

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
		'''
		The Constructor for loadLogDirectory Class
		
		logDirectory (String) : Contain path to create for log storage
		'''
		if not os.path.exists(logDirectory): os.makedirs(logDirectory)

class yum_operations():
	def __init__(self, auto_install=True, skip_broken=True, gpg_verify=True, refresh_db=True, enable_repo=[], disable_repo=[]):
		'''
		The Constructor for yum_operations Class
		
		Optional Args:
			auto_install (boolean, True)    : Automatically install packages used by "assumeyes"
			skip_broken  (boolean, True)    : Will skip if any failures in installation
			gpg_verify   (boolean, True)    : Enable GPG verification check(eg:--nogpgcheck)
			refresh_db   (boolean, True)    : Clean out the yum database before initializing
			enable_repo  (list,[])          : To enable the Repository
			disable_repo (list,[])          : To Disable the Repository
		Operation:
			YumBase()       : Initialize YumBase and setup attributes
			Distribution    : 'redhat' or 'centos' ...
			Major Version   : 6 or 7 or 8          ...
		'''
		execLog.debug('Object          - Created Class Object')
		
		self.disto			= platform.dist()[0]
		self.major_version 	= platform.dist()[1].split('.')[0]
		
		execLog.info('Distro           - {0}'.format(self.disto))
		execLog.info('OS Major Version - {0}'.format(self.major_version))
		
		try:
			self.yb						= yum.YumBase()
			self.yb.preconf.debuglevel 	= 0
			self.yb.preconf.errorlevel	= 0
			self.auto_install			= auto_install
			
			setattr(self.yb.conf, 'skip_broken', 	skip_broken)
			execLog.info('Set Skip Broken  - {0}'.format(skip_broken))
			
			setattr(self.yb.conf, 'assumeyes',		auto_install)
			execLog.info('Set Assume Yes   - {0}'.format(auto_install))
			
			if gpg_verify:
				setattr(self.yb.conf, 'gpgcheck', 	gpg_verify)
				execLog.info('Set GPG Check    - {0}'.format(gpg_verify))
			else:
				setattr(self.yb.conf, 'gpgcheck', 	not gpg_verify)
				execLog.info('Set GPG Check    - {0}'.format(not gpg_verify))
			
			if refresh_db:
				self.refresh_db()
			
			if enable_repo:
				for repo in enable_repo:
					self.yb.repos.enableRepo(repo)
					execLog.info('Enabled  Repo    - {0}'.format(repo))
			
			if disable_repo:
				for repo in disable_repo:
					self.yb.repos.disableRepo(repo)
					execLog.info('Disabled Repo    - {0}'.format(repo))
			
			execLog.info('YUM Base SetUP   - {0}'.format('YUM Base SetUp Completed'))
		except Exception as YumBaseError:
			execLog.error('Yum Base Object - ' + YumBaseError.__class__.__name__ + ' ' + str(YumBaseError).rstrip())
			exit(100)
	
	def refresh_db(self):
		'''
		Since yum refreshes the database automatically, this runs a yum clean,
		so that the next yum operation will have a clean database.
		
		CLI Example::
			salt '*' pkg.refresh_db
		'''
		try:
			execLog.info('YUM CleanUp      - CleanUp In Progress...')
			execLog.info('YUM Config File  - {0}'.format(self.yb.conf.config_file_path))
			execLog.info('YUM Log File     - {0}'.format(self.yb.conf.logfile))
			execLog.info('YUM Error Level  - {0}'.format(self.yb.conf.errorlevel))
			execLog.info('YUM CleanUp RPM  - {0}'.format(self.yb.cleanRpmDB()[1][0]))
			execLog.info('YUM CleanUp Cha  - {0}'.format(self.yb.cleanExpireCache()[1][0]))
			execLog.info('YUM CleanUp MD   - {0}'.format(self.yb.cleanMetadata()[1][0]))
			execLog.info('YUM CleanUP SQL  - {0}'.format(self.yb.cleanSqlite()[1][0]))
			execLog.info('YUM CleanUP PKG  - {0}'.format(self.yb.cleanPackages()[1][0]))
			execLog.info('YUM ChacheSetUp  - {0}'.format(self.yb.setCacheDir(force=True)))
			execLog.info('YUM CleanUp      - CleanUp Completed')
		except Exception as YumBaseError:
			execLog.error('Yum Base CleanUp : '+YumBaseError.__class__.__name__ + ' ' + str(YumBaseError).rstrip())
			exit(200)
	
	def _list_removed(self, old, new):
		'''
		List the packages which has been removed between the two package objects
		
		Args:
			old (boolean, True)	: Old Packages that are already available/installed
			new	(boolean, True)	: Old/Updated Packages that are recently installed
		Returns:
			pkgs (List)
		Ex:	'opkg'= {
						'current-version': new[npkg]
					}
		'''
		pkgs = {}
		for opkg in old:
			if opkg not in new:
				# pkgs.append(pkg)
				pkgs[opkg] = 	{
									'current-version': old[opkg]
								}
		return pkgs
	
	def _compare_versions(self, old, new):
		'''
		Returns a dict that that displays old and new versions for a package after 
		install/update of package.
		
		Args:
			old (boolean, True)	: Old Packages that are already available/installed
			new (boolean, True) : Old/Updated Packages that are recently installed
		Returns:
			pkgs	Dict
		Ex:	'npkg' ={
						'old-version'    : old[npkg],
						'current-version': new[npkg]
					}
		'''
		pkgs = {}
		for npkg in new:
			if npkg in old:
				if old[npkg] == new[npkg]:
					# if no change in the package
					continue
				else:
					# else the package was here before and the version has changed
					pkgs[npkg] = 	{
									'old-version': old[npkg],
									'current-version': new[npkg]
									}
			else:
				# if the package is freshly installed
				pkgs[npkg] 	= 	{
								'old-version': '',
								'current-version': new[npkg] 
								}
		return pkgs
	
	def list_upgrades(self, pkgs=[]):
		'''
		Check and list whether upgrade is available for the system or a package(s) mentioned
		
		Args:
			pkgs (List) : List the package(s) are available for update
		Returns:
			upgrade_list(Dict)
		CLI Example:
			salt '*' pkg.list_upgrades
		'''
		if pkgs:
			pkgs 		= self.list_pkgs(*pkgs)
		else:
			pkgs 		= self.list_pkgs()
		upgrade_list= {}
		
		# execLog.info('Pkgs for Upgrade - Generating the list...')
		for pkgtype in ['updates','available']:
			pl = self.yb.doPackageLists(pkgtype)
			for pkg in pkgs:
				# [] [] [] update any of these and check only 1st list
				exactmatch, matched, unmatched  = yum.packages.parsePackages(pl, [pkg])
				for package in exactmatch:
					upgrade_list.update({ package['name'] : { 'Installed' : pkgs[package['name']], 'Available-Update' : '-'.join([package['version'],package['release']]) }})
		
		# execLog.info('Pkgs for Upgrade - Completed the Process')
		return upgrade_list	
	
	def list_version(self, pkgs=[]):
		'''
		Returns a version if the package is installed else returns "Not Found !!!"
		
		Args:
			pkgs (List) : List of package(s) name to check the version
		Returns:
			Currently installed package(s) version(Dict)
				Ex : {'<package_name>': '<version>'}
		CLI Example::
			salt '*' pkg.version <package name>
		'''
		pkg_version = {}
		
		# execLog.info('Pkg Version list - {}'.format('Generating the list...'))
		for name in pkgs:
			pkg_v = self.list_pkgs(name)
			if name in pkg_v:
				pkg_version.update({ name : pkg_v[name] })
			else:
				pkg_version.update({name : 'Not Found !!!' })
		
		# execLog.info('Pkg Version list - Completed the Process')
		return pkg_version
	
	def list_pkgs(self, *args):
		'''
		List the package(s) that are currently installed in the system
		
		Optional Args:
			name (String | Empty) : String of package name to check the version
		Returns:
			Currently installed package(s) available_version(Dict)
				Ex : {'package': 'version'}
		CLI Example::
			salt '*' pkg.list_pkgs
		'''
		ts		= rpm.TransactionSet()
		pkgs	= {}
		
		# execLog.info('Pkg Version list - {}'.format('Generating the list...'))
		if len(args) == 0:
			# if no args are passed, will get details of all packages installed 
			for h in ts.dbMatch():
				pkgs[h['name']] = '-'.join([h['version'],h['release']])
		else:
			# get package version for each package in *args
			for arg in args:
				for h in ts.dbMatch('name', arg):
					pkgs[h['name']] = '-'.join([h['version'],h['release']])
		
		# execLog.info('Pkg Version list - Completed the Process')
		return pkgs
	
	def estimate_size(self, packages, block_size=4096):
		'''
		Estimate the installed size of a package list
		
		Args:
			packages   (list of TransactionMember objects) : Transaction objects created by yb.tsInfo
			block_size (int)                               : The default block(file) size
		Returns:
			The estimated size of installed packages(float in MB)
		
		Brief:
			Estimating actual requirements is difficult without the actual file sizes, which
			yum doesn't provide access to. So use the file count and block size to estimate
			a minimum size for each package.
		'''
		installed_size = 0		
		for p in packages:
			installed_size += len(p.po.filelist) * block_size
			installed_size += p.po.installedsize
		return float(format(installed_size/(1024*1024),'.3f'))

	def tnxn_mem_to_pack(self, tm):
		'''
		Extract the info from a TransactionMember object
		Args:
			tm(TransactionMember List)	: A Yum transaction member
		Returns:
			Dict with name, epoch, version, release, arch
		'''
		return 	{ tm.name : 
					{
					'current-version'	: tm.version + '-' + tm.release,
					}
				}
	
	def list_to_dict(self, list_of_dict, type):
		'''
		Converting a List of dict to Dict of Dict and adding status-type
		
		Args:
			list_of_dict (List of Dict) : List contain dicts
			type         (String)       : Types of status in string
		Returns:
			Dict of dict wit adding status-type in it
			Ex:
				{
				"python3-setuptools": {
					"current-version"	: "39.2.0-10.el7",
					"old-version"		: "38.2.0-10.el7",
					"status-type"		: "Main"
					}
				}
		'''
		dict_dict = {}
		for item in range(len(list_of_dict)):
			temp = list_of_dict.pop()
			for i in temp:
				temp[i]['status-type'] = type
			dict_dict.update(temp)
		return dict_dict
	
	def merge_dict(self, compare, package_installed={}, dependency_installed={}, failed={}, updated={}, removed={}):
		'''
		Merge two dicts _compare_versions or _list_removed with self.yb.tsInfo.*
		Which merges status-type to the dict
		
		Args:
			compare (Dict) :	Dict which is created by _compare_versions or _list_removed 
		Returns:
			Dict with new and old version
			Ex:
				{
					"python3-setuptools": {
						"current-version"	: "39.2.0-10.el7",
						"old-version"		: "38.2.0-10.el7",
						"status-type"		: "Main"
					}
				}
		'''
		for key in compare:
			for i in [package_installed,dependency_installed,failed,updated,removed]:
				if key in i:
					temp = compare[key]
					temp.update(i[key])
		return compare
	
	def yum_install(self, pkgs, **kwargs):
		'''
		Install the passed package(s) (yum install pkg -y)
		
		Args:
			pkgs (String) :	Comma separated name of the package(s) to be installed
		Returns:
			Dict with new and old version
			Ex:
				{
				"python3-setuptools": {
					"current-version"	: "39.2.0-10.el7",
					"old-version"		: "38.2.0-10.el7",
					"status-type"		: "Main"
					}
				}
		CLI Example::
			salt '*' pkg.install 'package package package'
		'''
		old 	= self.list_pkgs()
		
		for pkg in pkgs:
			try:
				self.yb.install(name=pkg)
				execLog.info('Installing Pkg   - {0}'.format(pkg))
			except yum.Errors.InstallError:
				execLog.info('Install Error on - {0}'.format(pkg))
				# log.error('Package {0} failed to install'.format(pkg))
				print 'Error'
				pass
		
		self.yb.resolveDeps()
		self.yb.buildTransaction()
		self.yb.tsInfo.makelists()
		
		package_size		 = self.estimate_size(self.yb.tsInfo.installed)
		dependency_size		 = self.estimate_size(self.yb.tsInfo.depinstalled)
		
		package_installed	 = self.list_to_dict(map(self.tnxn_mem_to_pack, self.yb.tsInfo.installed),'Main')
		dependency_installed = self.list_to_dict(map(self.tnxn_mem_to_pack, self.yb.tsInfo.depinstalled),'Dependency')
		failed				 = map(self.tnxn_mem_to_pack, self.yb.tsInfo.failed)
		
		if self.auto_install:
			self.yb.processTransaction(rpmDisplay=yum.rpmtrans.NoOutputCallBack())
		self.yb.closeRpmDB()
		
		new 	= self.list_pkgs()
		compare = self._compare_versions(old, new)
		return self.merge_dict(compare, package_installed, dependency_installed, failed)
	
	def yum_update(self, pkgs=[]):
		'''
		Run a full system upgrade(yum update -y)
		
		Returns:
			Dict with new and old version
		Ex :
			{
				"python3-setuptools": {
					"current-version"	: "39.2.0-10.el7",
					"old-version"		: "38.2.0-10.el7",
					"status-type"		: "Main"
				}
			}
		CLI Example::
			salt '*' pkg.upgrade
		'''
		old = self.list_pkgs()
		
		if pkgs:
			for pkg in pkgs:
				try:
					self.yb.update(name=pkg)
					execLog.info('Upgrading  Pkg   - {0}'.format(pkg))
				except yum.Errors.InstallError:
					execLog.info('Upgrade Fail for - {0}'.format(pkg))
					# log.error('Package {0} failed to install'.format(pkg))
					print 'Error'
					pass
		else:
			self.yb.update()
		
		self.yb.resolveDeps()
		self.yb.buildTransaction()
		self.yb.tsInfo.makelists()
		
		package_size		 = self.estimate_size(self.yb.tsInfo.installed)
		dependency_size		 = self.estimate_size(self.yb.tsInfo.depinstalled)
		updated_size		 = self.estimate_size(self.yb.tsInfo.updated)
		removed_size 		 = self.estimate_size(self.yb.tsInfo.removed)
		
		package_installed	 = self.list_to_dict(map(self.tnxn_mem_to_pack, self.yb.tsInfo.installed),'Main')
		dependency_installed = self.list_to_dict(map(self.tnxn_mem_to_pack, self.yb.tsInfo.depinstalled),'Dependency')
		failed				 = self.list_to_dict(map(self.tnxn_mem_to_pack, self.yb.tsInfo.failed),'Failure')
		updated				 = self.list_to_dict(map(self.tnxn_mem_to_pack, self.yb.tsInfo.updated),'updated')
		
		if self.auto_install:
			self.yb.processTransaction(rpmDisplay=yum.rpmtrans.NoOutputCallBack())
		self.yb.closeRpmDB()
		
		new 	= self.list_pkgs()
		compare = self._compare_versions(old, new)
		return self.merge_dict(compare, package_installed, dependency_installed, failed, updated)
	
	def yum_remove(self, pkgs):
		'''
		Removes packages(yum remove pkg -y) from the system
		
		Args:
			pkgs (String) :	Comma separated package(s) to be un-installed
		Returns:
			Return a Dict of package(s) removed
		Ex:
			{ "libtirpc": 
				{
				"current-version"	: "0.2.4-0.16.el7",
				"status-type"		: "Removed"
				}
			}
		CLI Example::
			salt '*' pkg.remove <package,package,package>
		'''
		old 	= self.list_pkgs(*pkgs)
		
		# same comments as in upgrade for remove.
		for pkg in pkgs:
			try:
				self.yb.remove(name=pkg)
				execLog.info('Removing the pkg - {0}'.format(pkg))
			except yum.Errors.InstallError:
				execLog.info('Remove Failure   - {0}'.format(pkg))
		
		self.yb.resolveDeps()
		self.yb.buildTransaction()
		self.yb.tsInfo.makelists()
		
		removed		 = self.estimate_size(self.yb.tsInfo.removed)
		
		failed	= self.list_to_dict(map(self.tnxn_mem_to_pack, self.yb.tsInfo.failed),'Failure')
		removed	= self.list_to_dict(map(self.tnxn_mem_to_pack, self.yb.tsInfo.removed),'Removed')
		
		if self.auto_install:
			self.yb.processTransaction(rpmDisplay=yum.rpmtrans.NoOutputCallBack())
		self.yb.closeRpmDB()
		
		new 	= self.list_pkgs(*pkgs)
		compare = self._list_removed(old, new)
		return self.merge_dict(compare, failed, removed)
	
	def print_json(self, dict):
		print json.dumps(dict, sort_keys=True, indent=4, separators=(' , ', '  :  '))

if __name__ == '__main__':
	'''
	Main Function 
	'''
	parser = argparse.ArgumentParser(description='Python script to Support YUM Operations')
	
	parser.add_argument('YAMLvarFile'		,action='store_const'	,help='Load Variables from Ansible'	,const='../ansible/vars/vars.yml'	)
	parser.add_argument('-auto_install'		,action='store_true'	,help='It will enable Assume Yes'	,default=False	,dest='auto_install')
	parser.add_argument('-skip_broken'		,action='store_true'	,help='Will skip if any failures'	,default=False	,dest='skip_broken'	)
	parser.add_argument('-gpg_verify'		,action='store_true'	,help='Skip the GPG verification'	,default=False	,dest='gpg_verify'	)
	parser.add_argument('-refresh_db'		,action='store_true'	,help='Clean out the yum database'	,default=False	,dest='refresh_db'	)
	parser.add_argument('-enable_repo'		,action='append'		,help='Enable the repository'		,default=[]		,dest='enable_repo'	)
	parser.add_argument('-disable_repo'		,action='append'		,help='Disable the repository'		,default=[]		,dest='disable_repo')
	parser.add_argument('-list_version'		,action='append'		,help='List of pkgs with version'	,default=[]		,dest='list_version')
	parser.add_argument('-list_version_all'	,action='store_true'	,help='List all pkgs with version'	,default=False	,dest='list_ver_all')
	parser.add_argument('-list_upgrade'		,action='append'		,help='List of pkgs with Upgrade'	,default=[]		,dest='list_upgrade')
	parser.add_argument('-list_upgrade_all'	,action='store_true'	,help='List all pkgs with Upgrade'	,default=False	,dest='list_upg_all')
	parser.add_argument('-yum_install'		,action='append'		,help='List of pkgs To Install'		,default=[]		,dest='yum_install'	)
	parser.add_argument('-yum_update'		,action='append'		,help='List of pkgs To Install'		,default=[]		,dest='yum_update'	)
	parser.add_argument('-yum_update_all'	,action='store_true'	,help='List all pkgs To Install'	,default=False	,dest='yum_upd_all'	)
	parser.add_argument('-yum_remove'		,action='append'		,help='List of pkgs To Un-Install'	,default=[]		,dest='yum_remove'	)
	
	# Disable Repo
	# arguments			= parser.parse_args(['-auto_install','-skip_broken','-gpg_verify','-refresh_db','-disable_repo','jenkins'])
	
	# Check and Upgrade
	# arguments			= parser.parse_args(['-list_version','python','-list_upgrade','python'])
	# arguments			= parser.parse_args(['-auto_install','-list_version','python','-list_upgrade','python','-yum_update','python'])
	
	# Everything
	# arguments			= parser.parse_args(['-auto_install','-skip_broken','-gpg_verify','-refresh_db','-list_version','python','-list_version','pythonn','-list_upgrade','python','-list_upgrade_all','-yum_install','jenkins','-yum_install','ansible','-yum_update','python','-yum_update_all','-yum_remove','jenkins','-yum_remove','ansible'])
	
	arguments			= parser.parse_args()
	YAMLvarFile			= arguments.YAMLvarFile
	auto_install		= arguments.auto_install
	skip_broken			= arguments.skip_broken
	gpg_verify			= arguments.gpg_verify
	refresh_db			= arguments.refresh_db
	enable_repo			= arguments.enable_repo
	disable_repo		= arguments.disable_repo
	
	list_version		= arguments.list_version
	list_version_all	= arguments.list_ver_all
	list_upgrade		= arguments.list_upgrade
	list_upgrade_all	= arguments.list_upg_all
	
	yum_install			= arguments.yum_install
	yum_update			= arguments.yum_update
	yum_update_all		= arguments.yum_upd_all
	yum_remove			= arguments.yum_remove
	
	# Load variables from ansible vars
	variables 		= global_vars.get_ansible_vars(YAMLvarFile)
	logDirectory 	= variables['scriptHomeDir']+'/'+variables['scriptsDir']+'/'+variables['logsDir']
	
	# Execute a class object to make log dir
	loadLogDirectory()
	print 'Created Log Directory : {0}'.format(logDirectory)
	
	# Define logging module, File Handler & Stream Handler
	# Define Log file name for later use
	execLogger		= 'yum-operations-logs' + time.strftime('-%Y-%m-%d-%Hh-%Mm-%Ss-%Z') + '.log'
	execLog			= logger.setupLogger('YUM Operation Steps', logDirectory +'/'+ execLogger)
	execLog.debug('Object          - Successfully Loadded Ansible Vars')
	
	# Creating class object
	yum_operations_all = yum_operations(auto_install=auto_install, skip_broken=skip_broken, gpg_verify=gpg_verify, refresh_db=refresh_db, enable_repo=enable_repo, disable_repo=disable_repo)
	# yum_operations_all = yum_operations(auto_install=True,disable_repo='jenkins')
	
	if list_version_all:
		print json.dumps(yum_operations_all.list_pkgs(), sort_keys=True, indent=4, separators=(' , ', '  :  '))
	
	if list_version:
		print json.dumps(yum_operations_all.list_version(list_version), sort_keys=True, indent=4, separators=(' , ', '  :  '))
	
	if list_upgrade:
		print json.dumps(yum_operations_all.list_upgrades(list_upgrade), sort_keys=True, indent=4, separators=(' , ', '  :  '))
	
	if list_upgrade_all:
		print json.dumps(yum_operations_all.list_upgrades(), sort_keys=True, indent=4, separators=(' , ', '  :  '))
	
	if yum_install:
		print json.dumps(yum_operations_all.yum_install(pkgs=yum_install), sort_keys=True, indent=4, separators=(' , ', '  :  '))
	
	if yum_update:
		print json.dumps(yum_operations_all.yum_update(pkgs=yum_update), sort_keys=True, indent=4, separators=(' , ', '  :  '))
	
	if yum_update_all:
		print json.dumps(yum_operations_all.yum_update(), sort_keys=True, indent=4, separators=(' , ', '  :  '))
	
	if yum_remove:
		print json.dumps(yum_operations_all.yum_remove(pkgs=yum_remove), sort_keys=True, indent=4, separators=(' , ', '  :  '))