#!/usr/bin/python2
# pip2 install pyyaml --user
# pip2 install requests --user

import yaml
import email
import requests
import argparse

def get_cloud_config_data(URL):
        # Try reaching the URL
        data_str  = ''
        request_status = requests.get(URL)
	
        # Check the status code
        # Add new line to the end of each line
        if request_status.status_code == 200:
                for line in request_status.iter_lines():
                        data_str += line + '\n'
                message = email.message_from_string(data_str)
	
	# Use Mail and YAML modules to convert the data
        # Walking through message
        # Confirm the content type
        for each_part in message.walk():
                if each_part.get_content_maintype() in ['multipart','text']:
                        if each_part.get_content_subtype() in ['cloud-config','plain']:
                                result_data = each_part.get_payload(decode=True)
				print result_data 
                                try:
                                        data = yaml.load(result_data,yaml.SafeLoader)
                                        return data
                                except yaml.YAMLError as yaml_exception:
                                        print yaml_exception
                else:
                        print "unable to get User-Data"
