#!/usr/bin/env python
# June 2019 - pcardot - proof of concept - How to create objects and rules from CSV file into FDM Managed Devices
'''
	get all ports object ( services ) previously created, display them and save them into service_objects.txt file
pcardot	
'''
import requests
import json
import yaml
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#version=2 # 2 :  for FTD 6.3
version=3 # 3 : for FTD 6.4 

def yaml_load(filename):
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
	
	request = requests.post("https://{}:{}/api/fdm/v{}/fdm/token".format(host, FDM_PORT,version),
						  json=payload, verify=False, headers=headers)
	if request.status_code == 400:
		raise Exception("Error logging in: {}".format(request.content))
	try:
		access_token = request.json()['access_token']
		return access_token
	except:
		raise

def fdm_get(host,token,url):
	'''
	This is a GET request take url, send it to device and return json result.
	'''
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"Authorization":"Bearer {}".format(token)
	}
	try:
		request = requests.get("https://{}:{}/api/fdm/v{}{}?limit=100".format(host, FDM_PORT,version,url),verify=False, headers=headers)
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
	# get token from token.txt
	fa = open("token.txt", "r")
	token = fa.readline()
	fa.close()
	#token = fdm_login(FDM_HOST,FDM_USER,FDM_PASSWORD) 
	print()
	print (" TOKEN :")
	print(token)
	print('======================================================================================================================================')	
	fa = open("service_objects.txt","w")   
	api_url="/object/tcpports"
	networks = fdm_get(FDM_HOST,token,api_url)
	#print(json.dumps(networks,indent=4,sort_keys=True))
	for line in networks['items']:
		print('name:', line['name'])
		print('value:', line['port'])
		print('description:', line['description'])
		print('type:', line['type'])
		print('id:', line['id'])
		print()
		#filter only object named  NEW_TCPxxxx 
		if line['name'].find("EW_TCP")==0:
			fa.write(line['name'])
			fa.write(';')			
			fa.write(line['port'])
			fa.write(';')   
			if line['description']==None:
				line['description']="No Description"
			fa.write(line['description'])
			fa.write(';')			
			fa.write(line['type'])
			fa.write(';')
			fa.write(line['id'])
			fa.write('\n')
	api_url="/object/udpports"
	networks = fdm_get(FDM_HOST,token,api_url)
	#print(json.dumps(networks,indent=4,sort_keys=True))
	for line in networks['items']:
		print('name:', line['name'])
		print('value:', line['port'])
		print('description:', line['description'])
		print('type:', line['type'])
		print('id:', line['id'])
		print()
		#filter only object named  NEW_UDPxxxx 
		if line['name'].find("NEW_UDP")==0:
			fa.write(line['name'])
			fa.write(';')			
			fa.write(line['port'])
			fa.write(';')   
			if line['description']==None:
				line['description']="No Description"
			fa.write(line['description'])
			fa.write(';')			
			fa.write(line['type'])
			fa.write(';')
			fa.write(line['id'])
			fa.write('\n')			
	fa.close()			
	
	
	