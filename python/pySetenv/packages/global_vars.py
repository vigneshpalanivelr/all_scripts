#!/usr/bin/python2

import yaml
import json
import argparse

def get_ansible_vars(YAMLvarFile):
	try:
		with open(YAMLvarFile) as var:
			return yaml.safe_load(var)
	
	except yaml.YAMLError as yaml_exception:
		raise ImportError(yaml_exception)
		exit(100)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Read ansible variables in YAML format')
	
	parser.add_argument('YAMLvarFile'		,action='store_const'		,help='Load Variables from Ansible Vars'	,const='../../../ansible/vars/vars.yml'	)
	
	arguments		= parser.parse_args()
	YAMLvarFile	= arguments.YAMLvarFile
	
	print json.dumps(get_ansible_vars(YAMLvarFile), sort_keys=True, indent=4)
