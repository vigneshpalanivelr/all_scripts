#!/usr/bin/python2
import re
import os
import sys
import argparse
import fileinput

#import custom modules
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv'))
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/pySetenv')
print sys.path
import userdata_template
import userdata_multipart

def get_all_groups(groups):
	for i in groups:
		for j in data[i]:
			data_groups = j.split(',')
		if i == 'ssh_groups':
			ssh_group_line = 'AllowGroups ' + ' '.join(data_groups)
		elif i == 'sudo_groups':
			sudo_group = data_groups
	return ssh_group_line, sudo_group

def change_sshd_config_replace(ssh_config_file, ssh_group_line=''):
	group_exp_replaced,passwd_yes_replaced,passwd_no_replaced,root_match_exp_replaced = False,False,False,False
	for line in fileinput.input(ssh_config_file, inplace=True):
		if ssh_group_line and group_exp.match(line):
			line = re.sub(r'(AllowGroups .*)',ssh_group_line,line)
			group_exp_replaced = True
		if passwd_no.match(line):
			line = re.sub(r'(PasswordAuthentication no)','PasswordAuthentication yes',line)
			passwd_yes_replaced = True
		if passwd_yes.match(line):
			line = re.sub(r'(#PasswordAuthentication yes)','#PasswordAuthentication no',line)
			passwd_no_replaced = True
		if root_match_exp.match(line):
			line = re.sub(r'(PermitRootLogin yes)','PermitRootLogin no',line)
			root_match_exp_replaced = True
		print line,
	
	for x in [ssh_group_line, 'PasswordAuthentication yes','PermitRootLogin no']:
		change_sshd_config_add(ssh_config_file, x)

def change_sshd_config_add(ssh_config_file, add_line):
	''' Below Script to write line if not found in whole file '''
	with open(ssh_config_file, 'a+') as file:
		if not any(add_line == x.strip() for x in file):
			file.write(add_line + '\n')

def change_sudoers(sudoers_file, ssh_group_line):
	with open(sudoers_file, 'a+') as file:
		if not any(group_exp.match(x.strip()) for x in file):
			file.write(ssh_group_line + '\n')

def add_sudo_file(sudoers_dir, sudo_group):
	if not os.path.exists(sudoers_dir):
		os.mkdir(sudoers_dir)
	for item in sudo_group:
		with open(sudoers_dir+'/my-sudoers-config', 'a+') as sudoers:
			if not any("%{item} \tALL=(ALL) \tNOPASSWD: ALL\n".format(item=item) == x for x in sudoers):
				sudoers.write("%{item} \tALL=(ALL) \tNOPASSWD: ALL\n".format(item=item))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Script to Update ssh and sudoers from User-Data')
	
	parser.add_argument('URL'		,action='store_const' ,const='http://169.254.169.254/latest/user-data'	,help='URL for User-Data')
	parser.add_argument('ssh_config_file'	,action='store_const' ,const='/etc/ssh/sshd_config'			,help='SSH Configuration file path')
	parser.add_argument('sudoers_dir'	,action='store_const' ,const='/etc/sudoers.d'				,help='Sudoers file path')
	parser.add_argument('sudoers_file'	,action='store_const' ,const='/etc/sudoers'				,help='Sudoers file path')
	
	# arguments	= parser.parse_args(['http://169.254.169.254/latest/user-data','/etc/ssh/sshd_config'])
	arguments	= parser.parse_args()
	URL		= arguments.URL
	ssh_config_file	= arguments.ssh_config_file
	sudoers_dir	= arguments.sudoers_dir
	sudoers_file	= arguments.sudoers_file
	
	group_exp	= re.compile(r'(AllowGroups .*)')
	passwd_no	= re.compile(r'(PasswordAuthentication n.*)')
	passwd_yes	= re.compile(r'(#PasswordAuthentication y.*)')
	root_match_exp	= re.compile(r'(PermitRootLogin y.*)')
	
	
	
	try:
		data = userdata_multipart.get_cloud_config_data(URL)
		# data = userdata_template.get_cloud_config_data(URL)
		try:
			ssh_group_line, sudo_group = get_all_groups(['ssh_groups','sudo_groups'])
			try:
				change_sshd_config_replace(ssh_config_file,ssh_group_line)
				# Enable If required
				# change_sudoers(sudoers_file, ssh_group_line)
				try:
					add_sudo_file(sudoers_dir, sudo_group)
				except Exception as change_sudoers_error:
					print change_sudoers_error
					exit(400)
			except Exception as change_sshd_config_error:
				print change_sshd_config_error
				exit(300)
		except Exception as get_groups_error:
			print get_groups_error
			exit(200)
	except Exception as data_error:
		print data_error
		exit(100)
