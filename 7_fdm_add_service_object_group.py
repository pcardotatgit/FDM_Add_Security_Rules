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
        if ( "object/network" in url ) or ( "object/tcpports" in url ) or ( "/object/udpports" in url ) or ( "/object/portgroups" in url ):
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


def get_services():
    '''
        GET all single service objects and all service object groups
        Print them
        Save result into a resulting CSV file
    '''
    fa = open("./temp/existing_service_objects.txt","w")     
    # get Port Object Groups
    api_url="/object/portgroups"
    offset=0
    go=1
    index=0
    while go:
        token=new_auth_token[0]
        services = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset,limit_global)
        #print(services)
        index=0
        if services.get('items'):
            for line in services['items']:
                existing_name_list.append(line['name'])    
                index+=1        
        if index>=limit_global:
            go=1
            offset+=index-1
        else:
            go=0                
    # get Single TCP Port Objects
    api_url="/object/tcpports"
    offset=0
    go=1
    index=0
    while go:    
        token=new_auth_token[0]
        services = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset,limit_global)
        #print(services)
        if services.get('items'):
            for line in services['items']:
                existing_name_list.append(line['name'])    
                index+=1    
        if index>=limit_global-1:
            go=1
            offset+=index-1
        else:
            go=0            
    # get Single UDP Port Objects        
    api_url="/object/udpports"
    offset=0
    go=1
    index=0
    while go==1:        
        token=new_auth_token[0]
        services = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset,limit_global)
        #print(services)
        if services.get('items'):
            for line in services['items']:
                existing_name_list.append(line['name'])    
                index+=1    
        if index>=limit_global-1:
            go=1
            offset+=index-1
        else:
            go=0    
    fi = open("./temp/existing_service_objects.txt", "w")    
    for nom in existing_name_list:    
        fi.write(nom)
        fi.write("\n")            
    fi.close()    
 
        
def get_port_types(token,version,username,password):
    '''
        retrieve port types for all service objects
    '''
    try:                
        # get Single TCP Port Objects
        api_url="/object/tcpports"
        port_list={}
        offset=0
        go=1
        index=0
        while go:    
            token=new_auth_token[0]
            services = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset,limit_global)
            #print(services)
            if services.get('items'):
                for line in services['items']:
                    port_list.update({line['name']:line['type']})
                    index+=1    
            if index>=limit_global-1:
                go=1
                offset+=index-1
            else:
                go=0            
        # get Single UDP Port Objects        
        api_url="/object/udpports"
        offset=0
        go=1
        index=0
        while go==1:        
            token=new_auth_token[0]
            services = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset,limit_global)
            #print(services)
            if services.get('items'):
                for line in services['items']:
                    port_list.update({line['name']:line['type']})   
                    index+=1    
            if index>=limit_global-1:
                go=1
                offset+=index-1
            else:
                go=0             
        return (port_list)
    except:
        raise            

def fdm_create_port_group(host,token,payload,version,username,password):
    '''
    This is a POST request to create a new servce object in FDM.
    '''
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
    }
    try:
        api_url="https://{}:{}/api/fdm/v{}/object/portgroups".format(host, FDM_PORT,version)
        request = requests.post(api_url,json=payload, headers=headers, verify=False)
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
            request = requests.post(api_url,json=payload, headers=headers, verify=False)
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

    
def read_csv(file,token,version,username,password):
    '''
    read csv file and generate  JSON Data to send to FTD device
    '''
    # get all type for all objects
    types=get_port_types(token,version,username,password)
    objects_details=[]
    with open (file) as csvfile:
        entries = csv.reader(csvfile, delimiter=';')
        for row in entries:
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
                the_type=types.get(objet)
                the_objet.update({"type":the_type})
                objets.append(the_objet)
            payload.update({"objects": objets})
            payload.update({"type": "portobjectgroup"})            
            objects_details.append(payload)
    return (objects_details)
    
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
    # let's initialize an error log file
    fh = open("error.log", "w")# we create a new empty error.log file
    fh.close()    
    print (yellow("first let's retreive all existing object names in order to avoid conflicts during object creation"))
    get_services()
    #print(existing_name_list)
    print (yellow("OK DONE ( Step 1 ) list saved in the ./temp/existing_service_objects.txt file",bold=True))           
    print('======================================================================================================================================')    
    print (yellow("Second let's read the csv file and add new objects into it"))    
    list=[]
    list=read_csv("./objects_csv_files/service_object_groups.csv",token,FDM_VERSION,FDM_USER,FDM_PASSWORD)
    print('======================================================================================================================================')    
    for objet in list:
        print("Adding new Port Object Group")
        print(objet)    
        token=new_auth_token[0]
        post_response = fdm_create_port_group(FDM_HOST,token,objet,FDM_VERSION,FDM_USER,FDM_PASSWORD)
        print(cyan(json.dumps(post_response,indent=4,sort_keys=True)))
        print('')    