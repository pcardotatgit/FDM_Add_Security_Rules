import sys
import requests
import yaml
import json
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from crayons import blue, green, white, red, yellow,magenta, cyan

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

def fdm_update_network_group(host,token,network_group_id,new_object_list,version,username,password):
    '''
    This is a PUT request to create to update an existing network object in FDM.
    '''
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
    }
    payload={
        'objects':new_object_list
        }
    print(red(payload,bold=True))
    #sys.exit()
    try:
        api_url="https://{}:{}/api/fdm/v{}/object/networkgroups/{}".format(host, FDM_PORT,version,network_group_id)
        print()
        print(api_url)
        print()
        request = requests.put(api_url,body=payload, headers=headers, verify=False)
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
    network_group_id='5c057565-dae9-11ed-84a8-f5811ede42c1'
    objects={'objects': [{'name': 'NEW_HOST-100.38.56.12', 'type': 'networkobject'}, {'name': 'NEW_HOST-PATRICK_LAPTOP', 'type': 'networkobject'}, {'name': 'NEW_HOST-WEB_SERVER', 'type': 'networkobject'}, {'name': 'NEW_HOST-10.37.1.9-32', 'type': 'networkobject'}]}   
    fdm_update_network_group(FDM_HOST,token,network_group_id,objects,FDM_VERSION,FDM_USER,FDM_PASSWORD) 