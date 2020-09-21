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

This script    displays and save into network_objects.txt file all network objects 
except  any-ipv4 and any-ipv6

'''
import requests
import json
import yaml
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from crayons import blue, green, white, red, yellow,magenta, cyan

# Second let's define some global variables
profile_filename="profile_ftd.yml"    
limit_global=1000 # number of object to retrieve in one single GET request
new_auth_token=['none']#as global variable in order to make it easily updatable

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
        if "object/network" in url:
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
        
def get_networks():
    '''
        GET all single network objects and all object groups
        Print them
        Save result into a resulting CSV file
    '''
    # Let's Create and Open a resulting file into which we will store all network objects and their details
    fa = open("./temp/network_objects.txt","w")   
    # List Network Object Groups First
    api_path="/object/networkgroups"
    # We read the network object list thanks to a loop which reads 1000 objects at each rounds.
    # Let's initialize the loop
    offset=0 # offset help us to specify at which position in the list we read the object list
    go=1 # used to stop the loop
    # Here under the network groups loop
    while go:       
        token=new_auth_token[0] # We refresh the initial variable which store the token in case of a token renewal during the last REST CALL
        networks = fdm_get(FDM_HOST,token,api_path,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset,limit_global)
        #print(json.dumps(networks,indent=4,sort_keys=True)) # print the JSON result in the console, into a indented readable format        
        index=0 # the number of objects we have read within the loop
        for item in networks['items']:
            # We print interesting keys for all network object items. 
            index+=1
            print('name:', item['name'])
            print('Type:', item['type'])
            print('value:')
            for item2 in item['objects']:        
                print('==',item2['name'])
            print('description:', item['description'])
            print('type:', item['type'])
            print('id:', item['id'])
            print('system object:', item['isSystemDefined']) # this keys is the keys which identifies System Objects. This is a boolean
            print()
            if ("utsideIPv4" not in item['name']) and ("ny-ipv" not in item['name']):# here is a basic example for filtering outputs based on strings contained into the object names
                # We save objects details into the resulting file
                fa.write(item['name'])
                fa.write(';GROUP;')
                for item2 in item['objects']:                
                    fa.write(item2['name'])
                    fa.write(',')
                fa.write(';')   
                if item['description']==None:
                    item['description']="No Description"
                fa.write(item['description'])
                fa.write(';')            
                fa.write(item['type'])
                fa.write(';')
                fa.write(item['id'])
                fa.write(';')
                fa.write(str(item['isSystemDefined']))# we must convert  the value into a string
                fa.write('\n')    # Write a [ new item ] character in the resulting file in order to avoid to ha all results into one single item
        if index>=limit_global-1:
            # index value is superior than the limit_global-1 value.  That means that we DON'T HAVE READ the entire table
            go=1 # just to confirm that we continue, this item is not mandatory
            offset+=index-1 # offset for the next round
        else:
            # index value is inferior than the limit_global-1 value.  That means that we HAVE READ the entire table
            go=0 # exit from the loop    
    # And then List Network Objects
    api_path="/object/networks"
    #token=new_auth_token[0] # We refresh the initial variable which store the token in case of a token renewal during the last REST CALL
    offset=0
    go=1
    index=0
    while go:    
        token=new_auth_token[0] # We refresh the initial variable which store the token in case of a token renewal during the last REST CALL
        networks = fdm_get(FDM_HOST,token,api_path,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset,limit_global)
        print(json.dumps(networks,indent=4,sort_keys=True))
        for item in networks['items']:
            index+=1
            print('name:', item['name'])
            print('Type:', item['subType'])
            print('value:', item['value'])
            print('description:', item['description'])
            print('type:', item['type'])
            print('id:', item['id'])
            print('system object:', item['isSystemDefined'])
            print()
            if ("utsideIPv4" not in item['name']) and ("ny-ipv" not in item['name']):
                fa.write(item['name'])
                fa.write(';')
                fa.write(item['subType'])
                fa.write(';')            
                fa.write(item['value'])
                fa.write(';')   
                if item['description']==None:
                    item['description']="No Description"
                fa.write(item['description'])
                fa.write(';')            
                fa.write(item['type'])
                fa.write(';')
                fa.write(item['id'])
                fa.write(';')
                fa.write(str(item['isSystemDefined']))                
                fa.write('\n')
        if index>=limit_global-1:
            go=1
            offset+=index-1
        else:
            go=0                
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
    get_networks()
    print(green("DONE ! The result is in the [ ./temp/network_objects.txt ] file ",bold=True))