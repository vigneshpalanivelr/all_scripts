#!/usr/bin/python2
import re
import os
import sys
import crypt
import argparse
import fileinput
import subprocess

#import custom modules
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv/variables'))
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv/packages'))
# sys.path.append(os.path.dirname('/root/all_scripts/python/pySetenv/variables/'))
# sys.path.append(os.path.dirname('/root/all_scripts/python/pySetenv/packages/'))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/pySetenv/variables/' )
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/pySetenv/packages/'  )
# import userdata_template
# import userdata_multipart
import logger
# print sys.path

def exec_command(command):
	try:
		process = subprocess.Popen(command, 
									stdin =subprocess.PIPE,
									stdout=subprocess.PIPE,
									stderr=subprocess.PIPE,
									universal_newlines=True,
									bufsize=0)
		while True:
			# Read output line by line
			# output = process.stdout.readline()
			# print(output.strip())
			# Poll and check the output ; .poll() function to check the return code of the process.
			# It will return None while the process is still running. 
			return_code = process.poll()
			if return_code is None:
				pass
			if return_code in [0,9]:
				# print('RETURN CODE', return_code)
				# Process has finished, read rest all the output 
				# for output in process.stdout.readlines():
					# print(output.strip())
				# print "{} : {} Successfully".format(group_name,msg)
				# print process.stderr.readlines()
				return True
			elif return_code in list(set(range(15))-set([0,9])):
				# print return_code
				exit(process.stderr.readlines())
	except Exception as groupCreation:
		print groupCreation
		exit(300)

def group_actions(action, group_name):
	if action == 'create': 
		if exec_command(['groupadd',group_name]):
			print "Created : Group : {}".format(group_name)
	elif action == 'delete':
		if exec_command(['groupdel',group_name]):
			print "Deleted : Group : {}".format(group_name)

def user_actions(action, user_name, user_pwd=None):
	if action == 'create': 
		encrypted_passwd = crypt.crypt(user_pwd)
		if exec_command(['useradd' ,'--password' ,encrypted_passwd ,user_name]):
			print "Created : User  : {}".format(user_name)
	elif action == 'delete':
		if exec_command(['userdel',user_name]):
			print "Deleted : User  : {}".format(user_name)

def add_remove_user(add_to_grp, group_name, user_name):
	if add_to_grp is True:
		if exec_command(['usermod' ,'-a','-G' ,group_name ,user_name]):
			print "Added   : {} To Group : {}".format(user_name,group_name)
	elif add_to_grp is False:
		if exec_command(['gpasswd' ,'-d' ,user_name ,group_name]):
			print "Removed : {} From Group : {}".format(user_name,group_name)

def validate_input(object, action, add_to_grp, group_name, user_name, user_pwd):
	if action == 'create':
		if object == 'all':
			if add_to_grp and group_name and user_name and user_pwd:
				print 'All Inputs are Validated'
			else:
				print 'Please provide Only 1)Username 2)Password 3)GroupName 4)Add-To-Grp'
				exit(1)
		elif object == 'user':
			if user_name and user_pwd and not add_to_grp and not group_name:
				print 'All Inputs are Validated'
			else:
				print 'Please provide Only 1)Username 2)Password'
				exit(1)
		elif object == 'group':
			if not user_pwd and group_name:
				print 'All Inputs are Validated'
			else:
				print 'Please provide Only 1)GroupName (Optional : 1)Username 2)Add-To-Group)'
				exit(1)
	elif action == 'delete':
		if object == 'all':
			if not add_to_grp and group_name and user_name and not user_pwd:
				print 'All Inputs are Validated'
			else:
				print 'Please provide Only 1)Username 2)GroupName'
				exit(1)
		elif object == 'user':
			if user_name and not user_pwd and not add_to_grp and not group_name:
				print 'All Inputs are Validated'
			else:
				print 'Please provide Only 1)Username'
				exit(1)
		elif object == 'group':
			if not user_name and not user_pwd and not add_to_grp and group_name:
				print 'All Inputs are Validated'
			else:
				print 'Please provide Only 1)GroupName'
				exit(1)
	if action == 'add':
		if object == 'map':
			if add_to_grp and group_name and user_name and not user_pwd:
				print 'All Inputs are Validated'
			else:
				print 'Please provide Only 1)Username 2)GroupName 3)Add-To-Grp'
				exit(1)
	if action == 'remove':
		if object == 'map':
			if not add_to_grp and group_name and user_name and not user_pwd:
				print 'All Inputs are Validated'
			else:
				print 'Please provide Only 1)Username 2)GroupName'
				exit(1)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Script to Add and Delete User and Group')
	
	parser.add_argument('object'		,action='store' ,choices=['user','group','map','all']		,help='Choose which need to create/delete'										)
	parser.add_argument('action'		,action='store' ,choices=['create','delete','add','remove'] ,help='Choose create/delete'													)
	parser.add_argument('--user_name'	,action='store' 											,help='Provide User Name'					,dest='user_name'					)
	parser.add_argument('--user_pwd'	,action='store' 											,help='Provide User Password'				,dest='user_pwd'					)
	parser.add_argument('--group_name'	,action='store' 											,help='Provide Group Name'					,dest='group_name'					)
	parser.add_argument('--add_to_grp'	,action='store_true'										,help='Checkbox to add using in Grp'		,dest='add_to_grp'	,default=False	)
	
	# arguments	= parser.parse_args(['all','create','--user_name','vignesh_test','--user_pwd','vignesh-test','--group_name','root_group','--add_to_grp'])
	# arguments	= parser.parse_args(['all','delete','--user_name','vignesh_test','--group_name','root_group'])
	# arguments	= parser.parse_args(['user','create','--user_name','vignesh_test','--user_pwd','vignesh-test'])
	# arguments	= parser.parse_args(['user','delete','--user_name','vignesh_test'])
	# arguments	= parser.parse_args(['group','create','--group_name','root_group'])
	# arguments	= parser.parse_args(['group','delete','--group_name','root_group'])
	# arguments	= parser.parse_args(['map','add','--user_name','vignesh_test','--group_name','root_group','--add_to_grp'])
	# arguments	= parser.parse_args(['map','remove','--user_name','vignesh_test','--group_name','root_group'])
	arguments	= parser.parse_args()
	object		= arguments.object
	action		= arguments.action
	user_name	= arguments.user_name
	user_pwd	= arguments.user_pwd
	group_name	= arguments.group_name
	add_to_grp	= arguments.add_to_grp
	
	validate_input(object, action, add_to_grp, group_name, user_name, user_pwd)
	
	if action == 'create':
		if object == 'all' or object == 'group':
			group_actions(action, group_name)
		if object == 'all' or object == 'user' and user_pwd:
			user_actions(action, user_name, user_pwd=user_pwd)
		if object == 'all' or add_to_grp is True:
			add_remove_user(add_to_grp, group_name, user_name)
	elif action == 'delete':
		if object == 'all' and add_to_grp is False:
			add_remove_user(add_to_grp, group_name, user_name)
		if object == 'all' or object == 'user':
			user_actions(action, user_name)
		if object == 'all' or object == 'group':
			group_actions(action, group_name)
	elif object == 'map' and action == 'add' and add_to_grp:
			add_remove_user(add_to_grp, group_name, user_name)
	elif object == 'map' and action == 'remove' and not add_to_grp:
			add_remove_user(add_to_grp, group_name, user_name)	
