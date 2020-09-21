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

from crayons import blue, green, white, red, yellow,magenta, cyan

# Second let's define some global variables
profile_filename="profile_ftd.yml"    
limit_global=1000 # number of object to retrieve in one single GET request
new_auth_token=['none']#as global variable in order to make it easily updatable
existing_name_list=[] # List of existing objects names into FTD

def yaml_load(filename):
    fh = open(filename, "r")
    yamlrawtext = fh.read()
    yamldata = yaml.load(yamlrawtext,Loader=yaml.FullLoader)
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
        fa = open("./temp/token.txt", "w")
        fa.write(access_token)
        fa.close()    
        new_auth_token[0]=access_token
        print (green("Token = "+access_token))
        print("Saved into token.txt file")        
        return access_token
    except:
        raise

def fdm_get(host,token,url,version,username,password,offset,limit):
    '''
    This is a GET request is now a generic get function.
    '''
    # Let's prepare the http header with the authentication token
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
    }
    try:
        #Let's build the api url
        # depending on the request api_path, we could need additionnal argument. Here under we have an example for network objects
        if ( "object/network" in url ) or ( "object/tcpports" in url ) or ( "/object/udpports" in url ) or ( "/object/portgroups" in url ) or ( "/object/portgroups" in url ):
            api_url="https://{}:{}/api/fdm/v{}{}?offset={}&limit={}".format(host, FDM_PORT,version,url,offset,limit)
        elif "some_string" in url:
            api_url="DEFINE THE API URL HERE"
        else:
            api_url="https://{}:{}/api/fdm/v{}{}".format(host, FDM_PORT,version,url)
         
        # send the REST CALL and store the JSON Result into the request variable         
        request = requests.get(api_url,verify=False, headers=headers)        
        # Store the status code
        status_code = request.status_code
        
        if status_code == 401: # Token is invalid !
            print(red("Auth Token invalid, Let\'s ask for a new one",bold=True))
            # We need username and password     for asking for a new authentication token            
            auth_token = fdm_login(host,username,password,version)
            # and then we can send again the REST CALL
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization":"Bearer {}".format(auth_token)
            }            
            request = requests.get(api_url,verify=False, headers=headers)
            status_code = request.status_code            
        return request.json()
    except:
        raise
        
def fdm_get_access_rules(api_url):
    '''
        GET all existing access rules
        Save result into a resulting CSV file
    '''
    # List Access Rules
    print ("getting all access rules. Max objects to retrieve : limit = {}".format(limit_global))
    access_rules_dict={}
    offset=0
    go=1
    while go:    
        token=new_auth_token[0] # We refresh the initial variable which store the token in case of a token renewal during the last REST CALL
        access_rules = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset,limit_global)        
        print(output)
        index=0
        if objects.get('items'):
            for line in objects['items']:   
                val = line['id']+'/'+line['type']
                service_dict.update({line['name']:val})                  
                index+=1    
        if index>=limit_global-1:
            go=1
            offset+=index-1
        else:
            go=0
    return(access_rules_dict)       
    
def get_policy():
    # STEP 1  Get the Policy ID , we need it as the parent ID for accessrules management    
    api_url="/policy/accesspolicies"
    accesspolicy = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,0,10)
    #print(json.dumps(accesspolicy,indent=4,sort_keys=True))
    data=accesspolicy['items']
    for entry in data:
       PARENT_ID=entry['id']
    print('PARENT ID ( needed for access policies ) = ')
    print(PARENT_ID)
    print()    
    fa = open("./temp/access_policies.txt","w")   
    token=new_auth_token[0]
    api_url="/policy/accesspolicies/"+PARENT_ID+"/accessrules"
    access_policies = fdm_get_access_rules(api_url)
    print(json.dumps(access_policies,indent=4,sort_keys=True))
    for line in access_policies['items']:
        print('name:', line['name'])    
        #print('sourceZones:', line['sourceZones'])
        # check if sourceZones empty
        if not line['sourceZones']:
            sourceZone='no'
        else:
            sourceZone=line['sourceZones'][0]['name']            
        print('sourceZones:', sourceZone)
        if not line['sourceNetworks']:
            sourceNetwork='no'
        else:
            sourceNetwork=line['sourceNetworks'][0]['name']
        print('sourceNetworks:', sourceNetwork)
        # check if destinationZones empty
        if not line['destinationZones']:
            destinationZone='no'
        else:
            destinationZone=line['destinationZones'][0]['name']            
        print('destinationZones:', destinationZone)        
        if not line['destinationNetworks']:
            destinationNetwork='no'
        else:
            destinationNetwork=line['destinationNetworks'][0]['name']                
        print('destinationNetworks:', destinationNetwork)        
        print('ruleAction:', line['ruleAction'])
        print('type:', line['type'])
        print('Id:', line['id'])
        #print('system object:', line['isSystemDefined'])
        print()
        # example to filter Access Rules by names
        #if line['name'].find("NEW_ACL")==0:
        if line['name'].find("Allow_all")==-1: #filter only non default Access rules
            fa.write(line['name'])
            fa.write(';')            
            fa.write(sourceZone)
            fa.write(';')         
            fa.write(destinationZone)
            fa.write(';')   
            fa.write(sourceNetwork)
            fa.write(';')             
            fa.write(destinationNetwork)
            fa.write(';')     
            fa.write(line['ruleAction'])
            fa.write(';')         
            fa.write(line['type'])
            fa.write(';')
            fa.write(str(line['id']))
            fa.write('\n')        
    fa.close()       
    
if __name__ == "__main__":
    #  load FDM IP & credentials here
    ftd_host = {}
    ftd_host = yaml_load(profile_filename)    
    pprint(ftd_host["devices"])    
    FDM_USER = ftd_host["devices"][0]['username']
    FDM_PASSWORD = ftd_host["devices"][0]['password']
    FDM_HOST = ftd_host["devices"][0]['ipaddr']
    FDM_PORT = ftd_host["devices"][0]['port']
    FDM_VERSION = ftd_host["devices"][0]['version']
    # get token from token.txt
    fa = open("./temp/token.txt", "r")
    token = fa.readline()
    fa.close()
    new_auth_token[0]=token # we store the token into a temporary variable in order to manage a potential token renewal between 2 REST CALLS
    print()
    print (" TOKEN :")
    print(token)
    print('======================================================================================================================================')
    api_url="/policy/accesspolicies/"+PARENT_ID+"/accessrules"
    fdm_get_access_rules(api_url)
