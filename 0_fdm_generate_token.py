# First import required python modules

import requests
import yaml
import json
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from crayons import blue, green, white, red, yellow,magenta, cyan

# Second let's define some global variables

profile_filename="profile_ftd.yml"
new_auth_token=['none']#as global variable in order to make it easily updatable

# thirdly let's defined some base function

def yaml_load(filename):
    '''
    load FTD device information for connection
    '''
    fh = open(filename, "r")
    yamlrawtext = fh.read()
    yamldata = yaml.load(yamlrawtext,Loader=yaml.FullLoader)
    return yamldata
    
def fdm_login(ipaddr,username,password,version):
    '''
    This is the normal login which will give you a ~30 minute session with no refresh.  
    '''
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer"
    }
    payload = {"grant_type": "password", "username": username, "password": password}
    
    request = requests.post("https://{}:{}/api/fdm/v{}/fdm/token".format(ipaddr, FDM_PORT,version),json=payload, verify=False, headers=headers)
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
        
def fdm_get_hostname(ipaddr,token,version):
    '''
    This is a GET request to obtain system's hostname. 
    We will use it to verify that the token we got works
    '''
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
    }
    try:
        request = requests.get("https://{}:{}/api/fdm/v{}/devicesettings/default/devicehostnames".format(ipaddr, FDM_PORT,version),
                           verify=False, headers=headers)
        return request.json()
    except:
        raise
        
# Here under our main function from which are called all above functions        
if __name__ == "__main__":
    #  load FDM IP & credentials here under
    ftd_host = {}
    ftd_host = yaml_load(profile_filename)    
    pprint(ftd_host["devices"])    
    FDM_USER = ftd_host["devices"][0]['username']
    FDM_PASSWORD = ftd_host["devices"][0]['password']
    FDM_IP_ADDR = ftd_host["devices"][0]['ipaddr']
    FDM_PORT = ftd_host["devices"][0]['port']
    FDM_VERSION = ftd_host["devices"][0]['version']
    
    token = fdm_login(FDM_IP_ADDR,FDM_USER,FDM_PASSWORD,FDM_VERSION)

    # save token into token.txt file

    fa = open("./temp/token.txt", "w")
    fa.write(token)
    fa.close()
    print()    
    print(yellow("BINGO ! You got a token ! :",bold=True))
    print()     
    print()     
    print ('==========================================================================================')
    print()
    x=input("Let's check it. Type Enter")
    hostname = fdm_get_hostname(FDM_IP_ADDR,token,FDM_VERSION)
    print ('JSON HOSTNAME IS =')
    print(json.dumps(hostname,indent=4,sort_keys=True))    
    print()
    print(green('  ===>  ALL GOOD !',bold=True))
    print()