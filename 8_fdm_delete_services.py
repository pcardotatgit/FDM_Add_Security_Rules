#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright (c) 2022 Cisco and/or its affiliates.

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

def delete_service_from_csv(host,token,file,version,username,password):
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
        nofirstline=0
        for row in entries:
            if nofirstline:            
            #print(row[0]+' : '+row[4]+' : '+str(row[3])+' : '+str(row[5]))
                try:
                    if row[5]=='False' and row[3]=='tcpportobject':
                        request = requests.delete("https://{}:{}/api/fdm/v{}/object/tcpports/{}".format(host, FDM_PORT,version,row[4]), headers=headers, verify=False)
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
                            request = requests.delete("https://{}:{}/api/fdm/v{}/object/tcpports/{}".format(host, FDM_PORT,version,row[4]), headers=headers, verify=False)
                            status_code = request.status_code
                        resp = request.text
                        if status_code == 200 or status_code == 201 or status_code == 202 or status_code == 204:
                            print (green("Delete was successful...",bold=True))
                            #json_resp = json.loads(resp)
                            #print(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
                        else :
                            request.raise_for_status()
                            print (red("Error occurred in Delete --> "+resp+' Status Code = '+str(status_code)))
                        
                        print("Single TCP Service Deleted")
                    elif row[5]=='False' and row[3]=='udpportobject':
                        request = requests.delete("https://{}:{}/api/fdm/v{}/object/udpports/{}".format(host, FDM_PORT,version,row[4]), headers=headers, verify=False)       
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
                            request = requests.delete("https://{}:{}/api/fdm/v{}/object/udpports/{}".format(host, FDM_PORT,version,row[4]), headers=headers, verify=False)
                            status_code = request.status_code
                        resp = request.text
                        if status_code == 200 or status_code == 201 or status_code == 202 or status_code == 204:
                            print (green("Delete was successful...",bold=True))
                            #json_resp = json.loads(resp)
                            #print(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
                        else :
                            request.raise_for_status()
                            print (red("Error occurred in Delete --> "+resp+' Status Code = '+str(status_code)))                                        
                        print("Single UDP Service Deleted")
                    elif row[5]=='False' and row[3]=='portobjectgroup':
                        request = requests.delete("https://{}:{}/api/fdm/v{}/object/portgroups/{}".format(host, FDM_PORT,version,row[4]), headers=headers, verify=False)       
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
                            request = requests.delete("https://{}:{}/api/fdm/v{}/object/portgroups/{}".format(host, FDM_PORT,version,row[4]), headers=headers, verify=False)
                            status_code = request.status_code
                        resp = request.text
                        if status_code == 200 or status_code == 201 or status_code == 202 or status_code == 204:
                            print (green("Delete was successful...",bold=True))
                            #json_resp = json.loads(resp)
                            #print(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
                        else :
                            request.raise_for_status()
                            print (red("Error occurred in Delete --> "+resp+' Status Code = '+str(status_code)))                            
                        print("Port Group Deleted")
                    else:
                        print(red('Nothing to delete !',bold=True))                
                except:
                    raise    
                #time.sleep(0.5)
            else:
                nofirstline=1                  
    return (1)        


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
    file="./temp/service_objects.txt"
    print("OBJECTS TO DELETE :")
    delete_service_from_csv(FDM_HOST,token,file,FDM_VERSION,FDM_USER,FDM_PASSWORD)
