# FDM_Add_Security_Rules

# FDM_6.4_quick_start

The goal of this project it to give some ready to use scripts for basic interactions with FDM managed FTD  device for 6.3 and 6.4 versions

These scripts allow you to :

profile_ftd.yml : define FTD device IP address and username / password needed to connect to it. This file will be loaded by all other scripts

version = 2 for FTD 6.3,  version = 3 for 6.4 , version = 4 for 6.5

0_ : Test connection to FTD and Generate an Authentication Token

1_ : Add new network objects to FTD Device from network_objects.csv file

1b_ : Add new network object groups to FTD Device from network_object_groups.csv file

2_ : Display and save into a texte file all previously created network objects

3_ : Delete all previously created network objects

4_ : Add new service objects to FTD Device from service_objects.csv file

4b_ : Add new service objects to FTD Device from port_object_groups.csv file

5_ : Display and save into a texte file all previously created service objects

6_ : Delete all previously created service objects

7_ : Add new Access Policies to FTD device from small_access_list.csv file

8_ : Display and save into the access_policies.txt file all previously created Access Policies

9_ : Delete all access Policies from the access_policies.txt file

100_ : Deploy last changes to FTD device

Every changes can be verified from FDM GUI