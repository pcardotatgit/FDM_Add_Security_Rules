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


This script	add all network objects groups from the network_object_groups.csv 
file into the FDM Device
	
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
limit=1000 # number of object to retrieve in one single GET request
existing_name_list=[] # List of existing names into FTD

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
	This is a GET request to obtain the list of all Network Objects in the system.
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

def fdm_create_network_group(host,token,payload,version,username,password):
	'''
	This is a POST request to create a new network object in FDM.
	'''
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"Authorization":"Bearer {}".format(token)
	}
	try:
		request = requests.post("https://{}:{}/api/fdm/v{}/object/networkgroups".format(host, FDM_PORT,version),
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
			request = requests.post("https://{}:{}/api/fdm/v{}/object/networks".format(host, FDM_PORT,version),
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
def convert_mask(ip):
	'''
	convert all mask formated  x.x.x.x  into  /x  ( ex: 255.255.255.0  => /24 )
	'''
	ip=ip.strip()
	liste=[]
	liste=ip.split(" ")
	address=liste[0]
	netmask=liste[1]
	newmask=sum(bin(int(x)).count('1') for x in netmask.split('.'))
	new_adress=address+'/'+str(newmask)
	return(new_adress)
	
def read_csv(file):
	'''
	read csv file and generate  JSON Data to send to FTD device
	'''
	donnees=[]
	with open (file) as csvfile:
		entries = csv.reader(csvfile, delimiter=';')
		for row in entries:
			#print (' print the all row  : ' + row)
			#print ( ' print only some columuns in the rows  : '+row[1]+ ' -> ' + row[2] )	
			if row[0] not in existing_name_list:
				row[1]=row[1].lower()
				payload = {}
				payload.update({"name":row[0]})
				payload.update({"description":row[3]})
				payload.update({"isSystemDefined": "false"})
				objets=[]	
				liste_objets=[]
				liste_objets=row[2].split(',')
				for objet in liste_objets:		
					the_objet={}
					the_objet.update({"name": objet})
					the_objet.update({"type":"networkobject"})
					objets.append(the_objet)
				payload.update({"objects": objets})
				payload.update({"type": "networkobjectgroup"})			
				donnees.append(payload)
				print(green("Adding => Object [{}] ".format(row[0]),bold=True))
			else:	
				print(red("Read CSV => Object [  {}   ] already exists in FMC we dont add it ".format(row[0]),bold=True))				
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

	fa = open("token.txt", "r")
	token = fa.readline()
	fa.close()
	new_auth_token[0]=token
	#print('TOKEN = ')
	#print(token)
	print('======================================================================================================================================')	
	print (yellow("first let's retreive all existing object names in order to avoid conflicts during object creation"))
	# List Network Groups
	print ("getting network object groups. Max objects to retrieve : limit = {}".format(limit))
	api_url="/object/networkgroups"
	offset=0
	go=1
	while go==1:	
		objets = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset)		
		#print(output)
		ii=0
		if objets.get('items'):
			for line in objets['items']:
				existing_name_list.append(line['name'])	
				ii+=1	
		if ii>=999:
			go=1
			offset+=ii-1
		else:
			go=0
	# List Network Addesses Objects ( host and ip addresses and ranges )
	print ("getting single network objects. Max objects to retrieve : limit = {}".format(limit))
	auth_token=new_auth_token[0]
	#print("1",auth_token)
	api_url="/object/networks"
	offset=0
	go=1
	while go==1:		
		objets = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset)
		#print(objets)
		ii=0
		if objets.get('items'):
			for line in objets['items']:
				existing_name_list.append(line['name'])	
				ii+=1	
		if ii>=999:
			go=1
			offset+=ii-1
		else:
			go=0
	fi = open("existing_network_objects.txt", "w")	
	for nom in 	existing_name_list:	
		fi.write(nom)
		fi.write("\n")			
	fi.close()
	#print(existing_name_list)
	print (yellow("OK DONE ( Step 1 ) list saved the existing_network_objects.txt file",bold=True))	
	print('======================================================================================================================================')	
	print (yellow("Second let's read the csv file and add new objects into it"))
	list=[]
	list=read_csv("network_object_groups.csv")	
	print('======================================================================================================================================')	
	for objet in list:
		print("Adding new network Object Group")
		print(objet)		
		token=new_auth_token[0]		
		post_response = fdm_create_network_group(FDM_HOST,token,objet,FDM_VERSION,FDM_USER,FDM_PASSWORD)
		print(json.dumps(post_response,indent=4,sort_keys=True))
		print('')	
