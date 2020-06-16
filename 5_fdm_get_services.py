#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright (c) 2019 Cisco and/or its affiliates.

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

This script gets all ports object ( services ) previously created, display them and 
save them into service_objects.txt file

'''
import requests
import json
import yaml
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from crayons import blue, green, white, red, yellow,magenta, cyan

new_auth_token=['none']#as global variable in order to make it easily updatable 
limit=1000 # number of object to retrieve in one single GET request

def yaml_load(filename):
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
	
	request = requests.post("https://{}:{}/api/fdm/v{}/fdm/token".format(host, FDM_PORT,version),
						  json=payload, verify=False, headers=headers)
	if request.status_code == 400:
		raise Exception("Error logging in: {}".format(request.content))
	try:
		access_token = request.json()['access_token']
		fa = open("token.txt", "w")
		fa.write(access_token)
		fa.close()	
		new_auth_token[0]=access_token
		print (green("Token = "+access_token))
		print("Saved into token.txt file")		
		return access_token
	except:
		raise

def fdm_get(host,token,url,version,username,password,offset):
	'''
	This is a GET request take url, send it to device and return json result.
	'''
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"Authorization":"Bearer {}".format(token)
	}
	try:
		request = requests.get("https://{}:{}/api/fdm/v{}{}?offset={}&limit={}".format(host, FDM_PORT,version,url,offset,limit),verify=False, headers=headers)
		status_code = request.status_code
		if status_code == 401: 
			print(red("Auth Token invalid, Let\'s ask for a new one",bold=True))
			fdm_login(host,username,password,version)
			line_content = []
			with open('token.txt') as inputfile:
				for line in inputfile:
					if line.strip()!="":	
						line_content.append(line.strip())						
			auth_token = line_content[0]
			#headers["Authorization"]="Bearer {}".format(auth_token)	
			headers = {
				"Content-Type": "application/json",
				"Accept": "application/json",
				"Authorization":"Bearer {}".format(auth_token)
			}			
			request = requests.get("https://{}:{}/api/fdm/v{}{}?offset={}&limit={}".format(host, FDM_PORT,version,url,offset,limit),verify=False, headers=headers)
			status_code = request.status_code
			
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
	# get token from token.txt
	fa = open("token.txt", "r")
	token = fa.readline()
	fa.close()
	new_auth_token[0]=token
	print()
	print (" TOKEN :")
	print(token)
	print('======================================================================================================================================')	
	fa = open("service_objects.txt","w") 	
	# get Port Object Groups
	api_url="/object/portgroups"
	token=new_auth_token[0]
	offset=0
	go=1
	ii=0
	while go==1:	
		networks = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset)
		print(json.dumps(networks,indent=4,sort_keys=True))
		for line in networks['items']:
			ii+=1
			print('name:', line['name'])
			for line2 in line['objects']:			
				print('==> name:', line2['name'])
			print('description:', line['description'])
			print('type:', line['type'])
			print('id:', line['id'])
			print('system object:', line['isSystemDefined'])
			print()
			#filter only object named  NEW_TCPxxxx 
			if line['isSystemDefined']==0:
				fa.write(line['name'])
				fa.write(';')
				for line2 in line['objects']:
					fa.write(line2['name'])
					fa.write(',')
				fa.write(';')   
				if line['description']==None:
					line['description']="No Description"
				fa.write(line['description'])
				fa.write(';')			
				fa.write(line['type'])
				fa.write(';')
				fa.write(line['id'])
				fa.write(';')
				fa.write(str(line['isSystemDefined']))							
				fa.write('\n')		
		if ii>=999:
			go=1
			offset+=ii-1
		else:
			go=0				
	# get Single TCP Port Objects
	api_url="/object/tcpports"
	token=new_auth_token[0]
	offset=0
	go=1
	ii=0
	while go==1:	
		networks = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset)
		print(json.dumps(networks,indent=4,sort_keys=True))
		for line in networks['items']:
			ii+=1
			print('name:', line['name'])
			print('value:', line['port'])
			print('description:', line['description'])
			print('type:', line['type'])
			print('id:', line['id'])
			print('system object:', line['isSystemDefined'])
			print()
			if line['isSystemDefined']==0:
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
				fa.write(';')
				fa.write(str(line['isSystemDefined']))			
				fa.write('\n')
		if ii>=999:
			go=1
			offset+=ii-1
		else:
			go=0			
	# get Single UDP Port Objects		
	api_url="/object/udpports"
	token=new_auth_token[0]
	offset=0
	go=1
	ii=0
	while go==1:		
		networks = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset)
		#print(json.dumps(networks,indent=4,sort_keys=True))
		for line in networks['items']:
			ii+=1
			print('name:', line['name'])
			print('value:', line['port'])
			print('description:', line['description'])
			print('type:', line['type'])
			print('id:', line['id'])
			print('system object:', line['isSystemDefined'])
			print()
			if line['isSystemDefined']==0:
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
				fa.write(';')
				fa.write(str(line['isSystemDefined']))				
				fa.write('\n')		
		if ii>=999:
			go=1
			offset+=ii-1
		else:
			go=0					
	fa.close()			
	
	
	