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

This script deletes all access policies contained into access_policies.txt


'''
import requests
import json
import yaml
import csv
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from crayons import blue, green, white, red, yellow,magenta, cyan

new_auth_token=['none']#as global variable in order to make it easily updatable 

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

def delete_access_policy_from_csv(host,token,file,parent_id,version,username,password):
	'''
	Delete every service object from the csv file
	'''
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"Authorization":"Bearer {}".format(token)
	}
	with open (file) as csvfile:
		entries = csv.reader(csvfile, delimiter=';')
		for row in entries:
			#print (' print the all row  : ' + row)
			#print ( ' print only some columuns in the rows  : '+row[1]+ ' -> ' + row[2] )	
			print(row[0]+' id = '+row[7])
			try:
				if row[0].find('NEW_')==0:
					request = requests.delete("https://{}:{}/api/fdm/v{}/policy/accesspolicies/{}/accessrules/{}".format(host, FDM_PORT,version,parent_id,row[7]), headers=headers, verify=False)  		
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
						request = requests.delete("https://{}:{}/api/fdm/v{}/policy/accesspolicies/{}/accessrules/{}".format(host, FDM_PORT,version,parent_id,row[7]), headers=headers, verify=False)
						status_code = request.status_code	
					resp = request.text
					if status_code == 200 or status_code == 201 or status_code == 202 or status_code == 204:
						print (green("Delete was successful...",bold=True))
						#json_resp = json.loads(resp)
						#print(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
					else :
						request.raise_for_status()
						print (red("Error occurred in Delete --> "+resp+' Status Code = '+str(status_code)))						
					print("Access Policy removed")
			except:
				raise			
	return (1)	
	
def fdm_get(host,token,url,version,username,password):
	'''
	generic GET request.
	'''
	headers = {
	   "Content-Type": "application/json",
	   "Accept": "application/json",
	   "Authorization":"Bearer {}".format(token)
	}
	try:

		request = requests.get("https://{}:{}/api/fdm/v{}{}?limit=100".format(host, FDM_PORT,version,url),verify=False, headers=headers)		
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
			request = requests.get("https://{}:{}/api/fdm/v{}{}?limit=100".format(host, FDM_PORT,version,url),verify=False, headers=headers)
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
	# STEP 1  Get the Policy ID , we need it as the parent ID for accessrules management	
	api_url="/policy/accesspolicies"
	accesspolicy = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD)
	#print(json.dumps(accesspolicy,indent=4,sort_keys=True))
	data=accesspolicy['items']
	for entry in data:
	   PARENT_ID=entry['id']
	print('PARENT ID ( needed for access policies ) = ')
	print(PARENT_ID)
	
	file="access_policies.txt"
	print("OBJECTS TO DELETE :")
	token=new_auth_token[0]
	delete_access_policy_from_csv(FDM_HOST,token,file,PARENT_ID,FDM_VERSION,FDM_USER,FDM_PASSWORD)
