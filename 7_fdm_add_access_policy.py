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

This script opens the small_access_list.csv file and add into the FDM Device all Access Policies 
contained into it

'''
import sys
import csv
import requests
import yaml
import json
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from crayons import blue, green, white, red, yellow,magenta, cyan

new_auth_token=['none']#as global variable in order to make it easily updatable 
limit=1000 # number of object ot get in on request

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
	   
def fdm_create_access_policy(host,token,payload,parent_id,version,username,password):
	'''
	This is a POST request to create a new access list.
	'''
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"Authorization":"Bearer {}".format(token)
	}
	try:
		request = requests.post("https://{}:{}/api/fdm/v{}/policy/accesspolicies/{}/accessrules".format(host, FDM_PORT,version,parent_id),
					json=payload, headers=headers, verify=False)
					
		status_code = request.status_code
		if status_code == 422: 
			print(red("Something went wrong . open the error.log file",bold=True))	
			print(red("Let's exit in order to debug Data",bold=True))
			print(cyan("Possible Causes : ",bold=True))
			print(cyan("Object Already Exists "))
			print(cyan("The payload is too large. "))
			print(cyan("The payload contains an unprocessable or unreadable entity such as a invalid attribut name or incorrect JSON syntax."))
			resp = request.text			
			print (red("Error occurred in POST --> "+resp,bold=True))
			fh = open("error.log", "a+")
			fh.write(resp)
			fh.write("\n")			
			fh.write("=========================================")
			fh.write("\n")
			fh.write(json.dumps(payload,indent=4,sort_keys=True))
			fh.close()
			#sys.exit()			
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
			request = requests.post("https://{}:{}/api/fdm/v{}/policy/accesspolicies/{}/accessrules".format(host, FDM_PORT,version,parent_id),
					json=payload, headers=headers, verify=False)
			status_code = request.status_code
		resp = request.text
		if status_code == 200 or status_code == 201 or status_code == 202:
			print (green("Post was successful...",bold=True))
			#json_resp = json.loads(resp)
			#print(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
		else :
			request.raise_for_status()
			print (red("Error occurred in POST --> "+resp+' Status Code = '+str(status_code)))							
		return request.json()
	except:
		raise
		
def fdm_get(host,token,url,version,username,password):
	'''
	generic GET request which call the url API and return the json result
	'''
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"Authorization":"Bearer {}".format(token)
	}
	try:
		request = requests.get("https://{}:{}/api/fdm/v{}{}?limit={}".format(host, FDM_PORT,version,url,limit),verify=False, headers=headers)
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
			request = requests.get("https://{}:{}/api/fdm/v{}{}?limit={}".format(host, FDM_PORT,version,url,limit),verify=False, headers=headers)
			status_code = request.status_code
			
		return request.json()
	except:
		raise  
	
def read_csv(file,networks:dict,tcpports:dict,udpports:dict):
	donnees=[]
	with open (file) as csvfile:
		entries = csv.reader(csvfile, delimiter=';')
		#print(tcpports)
		for row in entries:
			#print (' print the all row  : ' + row)
			print ( ' print only some columuns in the rows  : '+row[1]+ ' -> ' + row[2] )	
			all_network=networks['items']
			sourceID=''
			for item in all_network:
				if item['name']==row[2]:
					sourceID=item['id']
			destinationID=''		
			for item in all_network:
				if item['name']==row[3]:
					destinationID=item['id']					
			all_tcp_ports=tcpports['items']
			portID=''
			for item in all_tcp_ports:
				if item['name']==row[5]:
					portID=item['id']
			portID=portID.strip()
			if len(portID)==0:
				all_udp_ports=udpports['items']
				for item in all_udp_ports:
					if item['name']==row[5]:
						portID=item['id']  		
			payload = {
			  "name": row[0],
			  "description": row[6],
			  "ruleAction": row[1],			
			  "sourceNetworks": [
				{
				  "id":sourceID,
				  "type":"networkobject"				  
				}
			  ],
			  "destinationNetworks": [
				{
				  "id":destinationID,					
				  "type":"networkobject",				 
				}
			   ],
			  "destinationPorts": [
				{
				   "id":portID,
				   "type": "udpportobject"			   
				}					
			  ],				 
			  "type": "accessrule"
			}		   
			donnees.append(payload)
	return (donnees)
	
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
	print('TOKEN = ')
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
	print()
	#STEP 2 get all network objects IDs and put them in a dictionnary
	api_url="/object/networks"
	token=new_auth_token[0]
	network_objects_dict = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD)
	#STEP 3 get all service objects IDs and put them into 2 dictionnaries one for tcp and the other for udp
	api_url="/object/tcpports"
	token=new_auth_token[0]
	TCP_network_objects_dict = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD)
	api_url="/object/udpports"
	token=new_auth_token[0]
	UDP_network_objects_dict = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD)
	#STEP 4 read small_access_list.csv csv file
	list=[]
	list=read_csv("small_access_list.csv",network_objects_dict,TCP_network_objects_dict,UDP_network_objects_dict)	
	#STEP 5
	for objet in list:
		print(objet) 
		print() 
		#Add access Policy
		token=new_auth_token[0]
		post_response = fdm_create_access_policy(FDM_HOST,token,objet,PARENT_ID,FDM_VERSION,FDM_USER,FDM_PASSWORD)
		print(cyan(json.dumps(post_response,indent=4,sort_keys=True)))
		print('')	
		