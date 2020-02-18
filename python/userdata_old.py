#!/usr/bin/python2

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
                                        print data
                                except yaml.YAMLError as yaml_exception:
                                        print yaml_exception
                else:
                        print "unable to get User-Data"

if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='Script to read EC2 User-Data')
        parser.add_argument('URL'       ,action='store'	,default='http://169.254.169.254/latest/user-data'	,help='URL where the data resides')
	
        #arguments       = parser.parse_args(['http://169.254.169.254/latest/user-data'])
        arguments       = parser.parse_args()
        URL             = arguments.URL
	
        get_cloud_config_data(URL)
