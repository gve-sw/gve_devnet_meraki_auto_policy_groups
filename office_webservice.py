#
# Copyright (c) 2021 Cisco and/or its affiliates.
# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.1 (the "License"). You may obtain a copy of the
# License at
#                https://developer.cisco.com/docs/licenses
# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.
#

import tempfile
from pathlib import Path
import urllib.request
import uuid
import os

from meraki_connector import *
from config import api_key, base, org_id

############# Microsoft Web Service #####################
# Original Code taken from the Office Endpoints Web Service Overview then modified
# SOURCE: https://docs.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-ip-web-service?view=o365-worldwide


# helper to call the webservice and parse the response
def webApiGet(methodName, instanceName, clientRequestId):
    ws = "https://endpoints.office.com"
    requestPath = ws + '/' + methodName + '/' + instanceName + '?clientRequestId=' + clientRequestId
    request = urllib.request.Request(requestPath)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


# path where client ID and latest version number will be stored
# datapath = Path(tempfile.gettempdir() + '/endpoints_clientid_latestversion.txt') # If you want to store in temp file
datapath = Path(os.getcwd() + '/endpoints_clientid_latestversion.txt')  # Current directory

# fetch client ID and version if data exists; otherwise create new file
if datapath.exists():
    with open(datapath, 'r') as fin:
        clientRequestId = fin.readline().strip()
        latestVersion = fin.readline().strip()
else:
    clientRequestId = str(uuid.uuid4())
    latestVersion = '0000000000'
    with open(datapath, 'w') as fout:
        fout.write(clientRequestId + '\n' + latestVersion)

# call version method to check the latest version, and pull new data if version number is different
version = webApiGet('version', 'Worldwide', clientRequestId)
# version['latest'] = str(int(version['latest'])+1) # FOR DEMO PURPOSES, UNCOMMENT TO FAKE A NEW VERSION

# Initialize an array to store the data
cidrs = []
fqdns = []
ipv4_cidrs = []

if version['latest'] > latestVersion:
    print('New version of Office 365 worldwide commercial service instance endpoints detected')
    # write the new version number to the data file
    with open(datapath, 'w') as fout:
        fout.write(clientRequestId + '\n' + version['latest'])
    # invoke endpoints method to get the new data
    endpointSets = webApiGet('endpoints', 'Worldwide', clientRequestId)
    # filter results for Allow and Optimize endpoints, and transform these into tuples with port and category
    flatUrls = []
    for endpointSet in endpointSets:
        # if endpointSet['category'] in ('Optimize', 'Allow'):    # Similar logic can be used to filter by serviceArea
        if endpointSet['serviceArea'] in ('Skype'):  # Similar logic can be used to filter by serviceArea
            category = endpointSet['category']
            urls = endpointSet['urls'] if 'urls' in endpointSet else []
            tcpPorts = endpointSet['tcpPorts'] if 'tcpPorts' in endpointSet else ''
            udpPorts = endpointSet['udpPorts'] if 'udpPorts' in endpointSet else ''
            flatUrls.extend([(category, url, tcpPorts, udpPorts) for url in urls])
    flatIps = []
    allIps = []
    for endpointSet in endpointSets:
        if endpointSet['category'] in ('Optimize', 'Allow'):
            ips = endpointSet['ips'] if 'ips' in endpointSet else []
            category = endpointSet['category']
            # IPv4 strings have dots while IPv6 strings have colons
            ip4s = [ip for ip in ips if '.' in ip]  # ONLY IPv4 addresses
            tcpPorts = endpointSet['tcpPorts'] if 'tcpPorts' in endpointSet else ''
            udpPorts = endpointSet['udpPorts'] if 'udpPorts' in endpointSet else ''
            flatIps.extend([(category, ip, tcpPorts, udpPorts) for ip in ip4s])
            allIps.extend([(category, ip, tcpPorts, udpPorts) for ip in ips])

    print('IPv4 Firewall IP Address Ranges')
    ipv4_cidrs = ','.join(sorted(set([ip for (category, ip, tcpPorts, udpPorts) in flatIps])))
    print(ipv4_cidrs)

    print('URLs for Proxy Server')
    fqdns = ','.join(sorted(set([url for (category, url, tcpPorts, udpPorts) in flatUrls])))
    print(fqdns)

else:
    print('Office 365 worldwide commercial service instance endpoints are up-to-date')
    exit()

############# Meraki Processing #####################

# CSV strings into a lists
ipv4_cidrs = ipv4_cidrs.split(',')
fqdns = fqdns.split(',')

# Establish a UNIQUE prefix for this update - Here we use the Release Version from Microsoft
cidr_prefix = f"MSFT-CIDRs-v{version['latest']}"

# Set a policy object group name
cidr_policy_group_name = "MSFT-CIDRs"

# Add new policy objects
cidr_policy_request = List_to_Policy_Group(org_id, ipv4_cidrs, cidr_prefix, list_type='cidr',
                                           policy_group_name=cidr_policy_group_name)


# Repeat the same process for the FQDNs
fqdn_prefix = f"MSFT-FQDNs-v{version['latest']}"
fqdn_policy_group_name = "MSFT-FQDNs"
fqdn_policy_request = List_to_Policy_Group(org_id, fqdns, fqdn_prefix, list_type='fqdn',
                                           policy_group_name=fqdn_policy_group_name)

# Remove previous policy objects to reduce clutter (keep the policy GROUPS intact)
remove_previous_request = delete_matching_policy_objects(org_id, identifier=latestVersion)
