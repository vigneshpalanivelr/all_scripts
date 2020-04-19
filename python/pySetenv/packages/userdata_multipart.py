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
                                        try:
                                                data = yaml.load(result_data,yaml.SafeLoader)
                                                return data
                                        except yaml.YAMLError as yaml_exception:
                                                raise ImportError(yaml_exception)
        else:
                raise ImportError("Userdata is Empty : Please add some userdata......")

if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='Script to Update ssh and sudoers from User-Data')

        parser.add_argument('URL'               ,action='store_const' ,const='http://169.254.169.254/latest/user-data'  ,help='URL for User-Data')

        # arguments     = parser.parse_args(['http://169.254.169.254/latest/user-data'])
        arguments       = parser.parse_args()
        URL             = arguments.URL

        print get_cloud_config_data(URL)
