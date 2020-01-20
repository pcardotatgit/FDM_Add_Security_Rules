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

This script reads the service_objects.csv file and add into FTD all service objects contained into it


'''
import sys
import csv
import requests
import yaml
import json
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


def fdm_create_service(host,token,payload):
	'''
	This is a POST request take paylaod as the URL API to invoke.
	'''
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"Authorization":"Bearer {}".format(token)
	}
	try:
		if payload['protocol']=='tcp':
			del payload['protocol']
			print(payload)
			request = requests.post("https://{}:{}/api/fdm/v{}/object/tcpports".format(host, FDM_PORT,version),json=payload, headers=headers, verify=False)
		else:
			del payload['protocol']
			print(payload)
			request = requests.post("https://{}:{}/api/fdm/v{}/object/udpports".format(host, FDM_PORT,version),json=payload, headers=headers, verify=False)				 
		return request.json()
	except:
		raise

	
def read_csv(file):
	donnees=[]
	with open (file) as csvfile:
		entries = csv.reader(csvfile, delimiter=';')
		for row in entries:
			#print (' print the all row  : ' + row)
			#print ( ' print only some columuns in the rows  : '+row[1]+ ' -> ' + row[2] )	
			row[2]=row[2].lower()
			if row[2]=='tcp':
				payload = {
					"name":row[0],
					"description":row[4],
					"port":row[3],
					"type": "tcpportobject",
					"protocol":"tcp"
				}		
			else:
				payload = {
					"name":row[0],
					"description":row[4],
					"port":row[3],
					"type":"udpportobject",
					"protocol":"udp"					
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
	list=[]
	list=read_csv("service_objects.csv")
	# get token from token.txt
	fa = open("token.txt", "r")
	token = fa.readline()
	fa.close()
	#token = fdm_login(FDM_HOST,FDM_USER,FDM_PASSWORD)	 
	print('TOKEN = ')
	print(token)
	print('======================================================================================================================================')	
	for objet in list:
	   #print(objet)			   
		post_response = fdm_create_service(FDM_HOST,token,objet)
		print(json.dumps(post_response,indent=4,sort_keys=True))
		print('')	
