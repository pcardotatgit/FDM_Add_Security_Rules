# Add Security Rules into FirePOWER FDM Managed Device

## Quick start for creating objects and Security Rules into FDM

The goal of this project it to give some ready to use scripts for basic interactions with FDM managed FTD devices for any version starting from 6.3.

Objects and rules are ingested into the device from flat csv files.

These scripts allow you to :

- <b>profile_ftd.yml</b> : define FTD device IP address and username / password needed to connect to it. This file will be loaded by all other scripts

version = 2 for FTD 6.3,  version = 3 for 6.4 , version = 4 for 6.5

- <b>0_fdm_generate_token.py</b> : Test connection to FTD and Generate an Authentication Token. Stores it into the <b>token.txt</b>file
- <b>1_fdm_add_network_objects.py</b>: Add new network objects to FTD Device from <b>network_objects.csv</b> file
- <b>1b_fdm_add_network_object_group.py</b>: Add new network object groups to FTD Device from <b>network_object_groups.csv</b> file
- <b>2_fdm_get_networks</b>: Display and save into a texte file all previously created network objects
- <b>3_fdm_delete_networks.py</b> : Delete all previously created network objects
- <b>4_fdm_add_service_objects.py</b> : Add new service objects to FTD Device from service_objects.csv file
- <b>4b_fdm_add_service_object_group</b>: Add new service objects to FTD Device from <b>port_object_groups.csv</b> file
- <b>5_fdm_get_services.py</b :  and save into a texte file all previously created service objects
- <b>6_fdm_delete_services.py</b>: Delete all previously created service objects
- <b>7_fdm_add_access_policy.py</b>: Add new Access Policies to FTD device from small_access_list.csv file
- <b>8_fdm_get_access_policy.py</b>: Display and save into the access_policies.txt file all previously created Access Policies
- <b>9_fdm_delete_access_policies.py</b>: Delete all access Policies from the access_policies.txt file
- <b>100_fdm_deploy.py</b>: Deploy last changes to FTD device

Every changes can be verified from FDM GUI