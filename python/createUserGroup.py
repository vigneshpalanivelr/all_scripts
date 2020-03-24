#!/usr/bin/python2
import subprocess
import argparse

#import custom modules
# sys.path.append(os.path.dirname('/var/lib/jenkins/workspace/playbook-provisioning-job/all_scripts/python/pySetenv'))
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/pySetenv/variables')
sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/pySetenv/packages')
#print sys.path

def allUserActions(object, action, name):
	if action == 'add' and object == 'group':
		action = 'groupadd'
	elif action == 'delete' and object == 'group':
		action = 'groupdel'
	elif action == 'add' and object == 'user':
		action = 'useradd'
	elif action == 'delete' and object == 'user':
		action = 'userdel'
	process = subprocess.Popen([action, name], 
								stdin =subprocess.PIPE,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE,
								universal_newlines=True,
								bufsize=0)
	while True:
		# Read output line by line
		# output = process.stdout.readline()
		# print(output.strip())
		# Poll and check the output
		# .poll() function to check the return code of the process.
		# It will return None while the process is still running. 
		return_code = process.poll()
		if return_code is not None:
			print('RETURN CODE', return_code)
			# Process has finished, read rest all the output 
			for output in process.stdout.readlines():
				print(output.strip())
			break

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Script to Add and Delete User and Group')
	
	parser.add_argument('object'		,action='store' ,choices=['user','group']	                    ,help='Choose which need to create/delete')
	parser.add_argument('action'		,action='store' ,choices=['add','delete']	                    ,help='Choose create/delete')
	parser.add_argument('--user_name'	,action='store' 							,dest='user_name'	,help='Provide User Name')
	parser.add_argument('--group_name'	,action='store' 							,dest='group_name'	,help='Provide Group Name')
	
	arguments	= parser.parse_args(['group','delete','--user_name','vignesh-test'])
	object		= arguments.object
	action		= arguments.action
	user_name	= arguments.user_name
	group_name	= arguments.group_name
	
	try:
		if group_name:
			allUserActions(object ,action ,group_name)
			try:
				if user_name:
					allUserActions(object ,action ,user_name)
			except Exception as User_Creation_Err:
				print User_Creation_Err
				exit(200)
	except Exception as Group_Creation_Err:
		print Group_Creation_Err
		exit(100)
