# Add Security Rules into FirePOWER FDM Managed Device

## Quick start for creating objects and Security Rules into FDM

The goal of this project it to give some ready to use scripts for basic interactions with FDM managed FTD devices for any version starting from 6.3.

What we want to to here is to ingest Objects and rules into the device from flat csv files. That means that the only effort we have to do is to create these CSV files.

## Installation

Installing these script is pretty straight forward . You can just copy / and paste them into you python environment but a good practice is to run them into a python virtual environment.

### Install a Python virtual environment

	For Linux/Mac 

	<b>python3 -m venv venv</b>
	<b<source bin activate</b>

	For Windows 

	<b>virtualenv env </b>
	<b>\env\Scripts\activate.bat </b>

### git clone the scripts

	<b>git clone https://github.com/pcardotatgit/FDM_Add_Security_Rules.git</b>
	<b>cd FDM_Add_Security_Rules/</b>
	
## Running the scripts


First of all you have to enter the device access credentials into the b>profile_ftd.yml</b><br>

- <b>profile_ftd.yml</b> : define FTD device IP address and username / password needed to connect to it, and the FTD sofware version ( version = 2 for FTD 6.3,  version = 3 for 6.4 , version = 4 for 6.5, etc.. ).  This configuration file will be loaded by all other scripts.

Second you have to run the <b>0_fdm_generate_token.py</b> script. This in order to avoid in every script to ask for a new authentication token, the <b>0_fdm_generate_token.py</b> aks for a token and stores it into a text file named <b>token.txt</b>.  The generated token will be valid during 30 minutes and all next scripts will firt read this <b>token.txt</b> file for retrieving the token.

So running <b>0_fdm_generate_token.py</0> is mandatory after added credentials? 

## Here under the list of all scripts and their purposes

- <b>0_fdm_generate_token.py</b> : Test connection to FTD and Generate an Authentication Token. Stores it into the <b>token.txt</b>file
- <b>1_fdm_add_network_objects.py</b>: Add new network objects to FTD Device from <b>network_objects.csv</b> file
- <b>1b_fdm_add_network_object_group.py</b>: Add new network object groups to FTD Device from <b>network_object_groups.csv</b> file
- <b>2_fdm_get_networks</b>: Display and save into a texte file all previously created network objects
- <b>3_fdm_delete_networks.py</b> : Delete all previously created network objects
- <b>4_fdm_add_service_objects.py</b> : Add new service objects to FTD Device from service_objects.csv file
- <b>4b_fdm_add_service_object_group</b>: Add new service objects to FTD Device from <b>port_object_groups.csv</b> file
- <b>5_fdm_get_services.py</b> :  and save into a texte file all previously created service objects
- <b>6_fdm_delete_services.py</b>: Delete all previously created service objects
- <b>7_fdm_add_access_policy.py</b>: Add new Access Policies to FTD device from <b>small_access_list.csv</b> file
- <b>8_fdm_get_access_policy.py</b>: Display and save into the access_policies.txt file all previously created Access Policies
- <b>9_fdm_delete_access_policies.py</b>: Delete all access Policies from the access_policies.txt file
- <b>100_fdm_deploy.py</b>: Deploy last changes to FTD device

Every changes can be verified from FDM GUI