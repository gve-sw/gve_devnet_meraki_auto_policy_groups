# Automating Policy Object Group Creation with Meraki API
Automatically keep a Meraki policy objects group updated with a Web Service API. In this example, the Office IP and URL Webservice. Takes a list of either FQDNs or IPs, adds them as policy objects, and groups them as a policy object group in the Meraki dashboard. Policy object groups can be used to simplify rules in Meraki


## Contacts
* Andrew Dunsmoor (adunsmoo@cisco.com)

## Solution Components
* Meraki Dashboard
* Microsoft Office IP Address and URL Web Service (https://docs.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-ip-web-service?view=o365-worldwide)
## Installation/Configuration


Install the project dependencies with "pip install -r requirements.txt"


A config.py file must also be generated and completed. The required variables are as follows:

```python
#config.py
api_key = ""    # Meraki Dashboard API Key
base = 'https://api.meraki.com/api/v1'  #Meraki Dashboard URL
org_ig = '1234567'     # Meraki organization ID for your desired target org. 
```
If you don't know how to get your organization ID, follow these teps:
1. Log into the Meraki Dashboard (in the same browser)
2. Click on this URL: https://dashboard.meraki.com/api/v1/organizations
3. Find the organization you wish to configure and copy the ID. 


## Usage

This script pulls from the Microsoft Web Service Endpoints. However, the meraki_connector can be used more generally for any source to created and maintain policy object groups. 
Please note that this script was created while Policy Objects were in beta and not included in the Meraki SDK, which is why the requests library is used. 

Run the script with "python3 office_webservice.py" from your terminal. 

The script can also be scheduled as a Cron Job or using a scheduler: https://www.geeksforgeeks.org/schedule-a-python-script-to-run-daily/

Microsoft updates it's endpoints around once a month, and recommends you do not run a script against it's webservice more than once an hour. 
Daily is recommended.

Documentation for the Office IP and URL Web Service can be found here: https://docs.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-ip-web-service?view=o365-worldwide
  
### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.