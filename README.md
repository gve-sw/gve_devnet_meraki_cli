# gve_devnet_meraki_cli
This project is designed to interact with Meraki's API to manage and retrieve data across network devices in an organization. 
The core functionality revolves around retrieving configuration changes, managing network settings, and creating reports for audit and compliance purposes.


## Contacts
* Mark Orszycki

## Solution Components
* Meraki API
* Meraki MS

## Prerequisites
#### Meraki API Keys
In order to use the Meraki API, you need to enable the API for your organization first. After enabling API access, you can generate an API key. Follow these instructions to enable API access and generate an API key:
1. Login to the Meraki dashboard
2. In the left-hand menu, navigate to `Organization > Settings > Dashboard API access`
3. Click on `Enable access to the Cisco Meraki Dashboard API`
4. Go to `My Profile > API access`
5. Under API access, click on `Generate API key`
6. Save the API key in a safe place. The API key will only be shown once for security purposes, so it is very important to take note of the key then. In case you lose the key, then you have to revoke the key and a generate a new key. Moreover, there is a limit of only two API keys per profile.

> For more information on how to generate an API key, please click [here](https://developer.cisco.com/meraki/api-v1/#!authorization/authorization). 

> Note: You can add your account as Full Organization Admin to your organizations by following the instructions [here](https://documentation.meraki.com/General_Administration/Managing_Dashboard_Access/Managing_Dashboard_Administrators_and_Permissions).

## Installation/Configuration
1. Clone this repository with `git clone [repository name]`. To find the repository name, click the green `Code` button above the repository files. Then, the dropdown menu will show the https domain name. Click the copy button to the right of the domain name to get the value to replace [repository name] placeholder.
2. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/). Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).
3. Install the requirements with `pip3 install -r requirements.txt`
4. Navigate to the app directory: 
    ```bash
    cd app
    ```
5. The program is ready to run. The user will be prompted to enter there Meraki API key upon startup and it will be saved to the environment variables for future use in the app/config/.env file.
   
## Main Features & Usage
### Basic Use
Run the program with the following command to see all available options and parameters:
```bash
python main.py --help
```
### Get Configuration Changes Organization-Wide
The `get_config_changes_org_wide` command is the centerpiece of this application. 
It retrieves all configuration changes across every network within an organization for a specified timespan. 
The command supports filtering to focus only on switch changes, making it highly relevant for organizations looking to audit changes in their network configurations.

**Usage:**
```bash
python main.py get_config_changes_org_wide --api_key=<API_KEY> --timespan=<TIMESPAN> --filter_switch
```

*Note*: The `--timespan` argument is optional and defaults to 1 day. The `--filter_switch` argument is also optional and defaults to False. 
*Note*: If you do not provide the Meraki API key, the program will look for the API key in the environment variables; If one is found, the user will be prompted
which key they would like to use. IF no key is found, the user will be prompted to enter a key & it will be saved to the environment variables for future use in the app/config/.env file.


## Other Features
### Get Configuration Changes by Network
Retrieves configuration changes for a specific network within a specified timespan. If no network ID is provided, the program will prompt the user to select a network from a list of available networks.
**Usage:**
```bash
python main.py get_config_changes_by_network --api_key=<API --network_id=<NETWORK_ID> --timespan=<TIMESPAN>
```

### Get Configuration Changes Network List
Fetches configuration changes for a list of specified networks over a given timespan. To use this command, you must provide a list of network IDs separated by commas in the settings.py file:
```python
TARGET_NETWORKS = ["", "", ""]
```
**Usage:**
```bash
python main.py get_config_changes_network_list --api_key=<API_KEY> --timespan=<TIMESPAN> --t0=<START_TIME> --t1=<END_TIME> --filter_switch
```     


### List Organizations
The `list_organizations` command retrieves a list of all organizations associated with the provided API key and saves the Key & associated organization ID to .env:
**Usage:**
```bash
python main.py list_orgs --api_key=<MERAKI_API_KEY>
```

### List Networks
The `list_networks` command retrieves a list of all networks associated with the provided organization ID:
**Usage:**
```bash
python main.py list_networks --api_key=<MERAKI_API_KEY> --org_id=<ORG_ID>
``` 

### Create Network
The `create_network` command creates a new network within the specified organization:
**Usage:**
```bash
python main.py create_org --api_key=<API_KEY>
```

### Create Organization
The `create_organization` command creates a new organization in your Meraki dashboard:
**Usage:**
```bash
python main.py create_org --api_key=<API_KEY>
```


# Screenshots/Gifs
### Fetching Configuration Changes for all Switches in Meraki Organization: <br>
![/IMAGES/main.gif](/IMAGES/main.gif)<br>

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.






