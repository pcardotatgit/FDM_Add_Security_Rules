#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

This script connects to your device. Negociate a token, save it to the token.txt file .
The token.txt file will be read by all other scripts in order to get the token value. 
The token is valid 30 minutes. 
This script must be runt in order to get a 30 minutes valid token

As a check this script Retrieves the device's hostname and displays it.  This confirm that the 
connexion to the FDM device succeeded

First Edit the profile_ftd.yml file and save your FTD device's IP address , admin user name and password

'''
import requests
import yaml
import json
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from crayons import blue, green, white, red, yellow,magenta, cyan
	
def yaml_load(filename):
	'''
	load device information for connection
	'''
	fh = open(filename, "r")
	yamlrawtext = fh.read()
	yamldata = yaml.load(yamlrawtext)
	return yamldata
	
def fdm_login(host,username,password,version):
	'''
	This is the normal login which will give you a ~30 minute session with no refresh.  
	Should be fine for short lived work.  
	Do not use for sessions that need to last longer than 30 minutes.
	'''
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"Authorization":"Bearer"
	}
	payload = {"grant_type": "password", "username": username, "password": password}
	
	request = requests.post("https://{}:{}/api/fdm/v{}/fdm/token".format(host, FDM_PORT,version),json=payload, verify=False, headers=headers)
	if request.status_code == 400:
		raise Exception("Error logging in: {}".format(request.content))
	try:
		access_token = request.json()['access_token']
		return access_token
	except:
		raise
		
def fdm_get_hostname(host,token,version):
	'''
	This is a GET request to obtain system's hostname.
	'''
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"Authorization":"Bearer {}".format(token)
	}
	try:
		request = requests.get("https://{}:{}/api/fdm/v{}/devicesettings/default/devicehostnames".format(host, FDM_PORT,version),
						   verify=False, headers=headers)
		return request.json()
	except:
		raise
		
if __name__ == "__main__":
	#  load FMC IP & credentials here
	ftd_host = {}
	ftd_host = yaml_load("profile_ftd.yml")	
	pprint(ftd_host["devices"])	
	#pprint(fmc_host["devices"][0]['ipaddr'])
	FDM_USER = ftd_host["devices"][0]['username']
	FDM_PASSWORD = ftd_host["devices"][0]['password']
	FDM_HOST = ftd_host["devices"][0]['ipaddr']
	FDM_PORT = ftd_host["devices"][0]['port']
	FDM_VERSION = ftd_host["devices"][0]['version']
	token = fdm_login(FDM_HOST,FDM_USER,FDM_PASSWORD,FDM_VERSION)
	'''
	save token into token.txt file
	'''
	fa = open("token.txt", "w")
	fa.write(token)
	fa.close()
	print()	
	print(yellow("BINGO ! You got a token ! :",bold=True))
	print()	
	print() 
	print(green(token,bold=True))
	print()  
	print() 	
	print ('==========================================================================================')
	print()
	hostname = fdm_get_hostname(FDM_HOST,token,FDM_VERSION)
	print ('JSON HOSTNAME IS =')
	print(json.dumps(hostname,indent=4,sort_keys=True))	
	print()
	print(green('  ===>  ALL GOOD !',bold=True))
	print()