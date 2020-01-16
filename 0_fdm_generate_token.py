#!/usr/bin/env python
# June 2019 - pcardot - proof of concept - How to create objects and rules from CSV file into FDM Managed Devices
'''
Edit profile_ftd.yml file and save your FTD device's IP address , admin user name and password

This script connects to your device. Negociate a token, save it to the token.txt for it to be used 

Retrieves the device's hostname and displays it.  This confirm that the connexion succeeded

pcardot
'''
import requests
import yaml
import json
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#version=2 # 2 :  for FTD 6.3
version=3 # 3 : for FTD 6.4 
	
def yaml_load(filename):
	'''
	load device information for connection
	'''
	fh = open(filename, "r")
	yamlrawtext = fh.read()
	yamldata = yaml.load(yamlrawtext)
	return yamldata
	
def fdm_login(host,username,password):
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
	token = fdm_login(FDM_HOST,FDM_USER,FDM_PASSWORD)
	api_version=3
	'''
	save token into token.txt file
	'''
	fa = open("token.txt", "w")
	fa.write(token)
	fa.close()
	print()	
	print("BINGO ! You got a token ! :")
	print()	
	print() 
	print(token)
	print()  
	print() 	
	print ('==========================================================================================')
	print()
	hostname = fdm_get_hostname(FDM_HOST,token,api_version)
	print ('JSON HOSTNAME IS =')
	print(json.dumps(hostname,indent=4,sort_keys=True))	
	print()
	print('  ===>  ALL GOOD !')
	print()