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


This script add all network objects from the network_objects.csv file

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
existing_name_list=[] # List of existing network objects names into FTD

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
 
def get_existing_networks():
    '''
        GET all existing network objects 
        Save result into a resulting CSV file
    '''
    # List Network Groups
    print ("getting network object groups. Max objects to retrieve : limit = {}".format(limit_global))
    api_url="/object/networkgroups"
    offset=0
    go=1
    while go:    
        token=new_auth_token[0] # We refresh the initial variable which store the token in case of a token renewal during the last REST CALL
        objects = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset,limit_global)        
        #print(output)
        index=0
        if objects.get('items'):
            for line in objects['items']:
                existing_name_list.append(line['name'])    
                index+=1    
        if index>=limit_global-1:
            go=1
            offset+=index-1
        else:
            go=0
    # List Network Addesses Objects ( host and ip addresses and ranges )
    print ("getting single network objects. Max objects to retrieve : limit = {}".format(limit_global))    
    api_url="/object/networks"
    offset=0
    go=1
    while go==1:
        auth_token=new_auth_token[0]    
        objects = fdm_get(FDM_HOST,token,api_url,FDM_VERSION,FDM_USER,FDM_PASSWORD,offset,limit_global)
        #print(objects)
        index=0
        if objects.get('items'):
            for line in objects['items']:
                existing_name_list.append(line['name'])    
                index+=1    
        if index>=limit_global-1:
            go=1
            offset+=index-1
        else:
            go=0
    fi = open("./temp/existing_network_objects.txt", "w")    
    for nom in     existing_name_list:    
        fi.write(nom)
        fi.write("\n")            
    fi.close()    
    
def fdm_create_network(host,token,payload,version,username,password):
    '''
    This is a POST request to create a new network object in FDM.
    '''
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
    }
    try:
        api_url="https://{}:{}/api/fdm/v{}/object/networks".format(host, FDM_PORT,version)
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
            # write the error output and payload which generate the error in the error log file
            fh = open("error.log", "a+")
            fh.write(resp)
            fh.write("\n")            
            fh.write("=========================================")
            fh.write("\n")
            fh.write(json.dumps(payload,indent=4,sort_keys=True))
            fh.close()            
        if status_code == 200:
            print (green("Post was successful...",bold=True))
            #print(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
        else :
            resp = request.text
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
    if len(liste)>1:
        netmask=liste[1]
        newmask=sum(bin(int(x)).count('1') for x in netmask.split('.'))
        new_adress=address+'/'+str(newmask)
    else:
        new_adress=address
    return(new_adress)
    
def read_csv(file):
    '''
    read csv file and generate  JSON Data to send to FTD device
    '''
    objects_details=[]
    with open (file) as csvfile:
        entries = csv.reader(csvfile, delimiter=';')
        for row in entries:
            if row[0] not in existing_name_list:            
                row[1]=row[1].lower()
                if row[1]=='host':
                    payload = {
                        "name":row[0],
                        "description":row[3],
                        "subType":"HOST",
                        "value":row[2],
                        "type":"networkobject"
                    }
                elif row[1]=='fqdn':
                    payload = {
                        "name":row[0],
                        "description":row[3],
                        "subType":"FQDN",
                        "value":row[2],
                        "type":"networkobject"
                    }                    
                elif row[1]=='subnet':
                    new_adress=convert_mask(row[2])
                    payload = {
                        "name":row[0],
                        "description":row[3],
                        "subType":"NETWORK",
                        "value":new_adress,
                        "type":"networkobject"
                    }
                else:
                    payload = {
                        "name":row[0],
                        "description":row[3],
                        "subType":"RANGE",
                        "value":row[2],
                        "type":"networkobject"
                    }                
                objects_details.append(payload)
                print(green("Adding => Object [{}] ".format(row[0]),bold=True))
            else:    
                print(red("Read CSV => Object [  {}   ] already exists in FTD. We dont add it ".format(row[0]),bold=True))                
    return (objects_details)
    
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
        api_url="https://{}:{}/api/fdm/v{}/object/networkgroups".format(host, FDM_PORT,version)
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
            print(cyan("The payload contains an unprocessable : Missing Network Object."))
            resp = request.text            
            print (red("Error occurred in POST --> "+resp,bold=True))
            fh = open("error.log", "a+")
            fh.write(resp)
            fh.write("\n")            
            fh.write("=========================================")
            fh.write("\n")
            fh.write(json.dumps(payload,indent=4,sort_keys=True))
            fh.close()
        if status_code == 200:
            print (green("Post was successful...",bold=True))
            #json_resp = json.loads(resp)
            #print(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
        else :
            resp = request.text
            request.raise_for_status()
            print (red("Error occurred in POST --> "+resp+' Status Code = '+str(status_code)))    
            
        return request.json()
    except:
        raise

def read_group_csv(file):
    '''
    read csv file and generate  JSON Data to send to FTD device
    '''
    objects_details=[]
    with open (file) as csvfile:
        entries = csv.reader(csvfile, delimiter=';')
        for row in entries:
            if row[0] not in existing_name_list:
                row[1]=row[1].lower()
                payload = {}
                payload.update({"name":row[0]})
                payload.update({"description":row[3]})
                payload.update({"isSystemDefined": "false"})
                objects=[]    
                objects_list=[]
                objects_list=row[2].split(',')
                for object in objects_list:        
                    the_objet={}
                    the_objet.update({"name": object})
                    the_objet.update({"type":"networkobject"})
                    objects.append(the_objet)
                payload.update({"objects": objects})
                payload.update({"type": "networkobjectgroup"})            
                objects_details.append(payload)
                print(green("Adding => Object [{}] ".format(row[0]),bold=True))
            else:    
                print(red("Read CSV => Object [  {}   ] already exists in FMC we dont add it ".format(row[0]),bold=True))                
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
    print('====================================================================================================')    
    # let's initialize an error log file
    fh = open("error.log", "w")# we create a new empty error.log file
    fh.close()
    print (yellow("first let's retreive all existing object names in order to avoid conflicts during object creation"))
    get_existing_networks()
    #print(existing_name_list)
    print (yellow("OK DONE ( Step 1 ) list saved the ./temp/existing_network_objects.txt file",bold=True))    
    print('====================================================================================================')
    print (yellow("Second let's read the csv file and add new objects into a list"))
    list=[]
    list=read_group_csv("./objects_csv_files/network_object_groups.csv")    
    print('======================================================================================================================================')    
    for objet in list:
        print("Adding new network Object Group")
        print(objet)        
        token=new_auth_token[0]        
        post_response = fdm_create_network_group(FDM_HOST,token,objet,FDM_VERSION,FDM_USER,FDM_PASSWORD)
        print(json.dumps(post_response,indent=4,sort_keys=True))
        print('')    
    print(green("OK ALL DONE",bold=True))