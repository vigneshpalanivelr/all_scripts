#!/usr/bin/python2

import yaml
import requests
import argparse

def get_cloud_config_data(URL='http://169.254.169.254/latest/user-data'):
        # Try reaching the URL
        data_str  = ''
        request_status = requests.get(URL)
	
        # Check the status code
        # Add new line to the end of each line
        if request_status.status_code == 200:
                for line in request_status.iter_lines():
                        data_str += line + '\n'
		
		# Use YAML module to convert the string data to YAML
		try:
			data = yaml.load(data_str ,yaml.SafeLoader)
			return data
		except yaml.YAMLError as yaml_exception:
			print yaml_exception
			raise Exception("Error : Unable to get User-Data from URL : {}".format(URL))
        else:
                return "Error : Unable to get User-Data"
