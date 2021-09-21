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


import pprint
import feedparser
import json
import time
import meraki
import requests
from config import api_key, base, org_id

## Policy Object GROUPS ##

def get_policy_objects_groups(organizationId):
    url = base+f'/organizations/{organizationId}/policyObjects/groups'
    headers = {
        "Content-Type": "application/json",
        "X-Cisco-Meraki-API-KEY": api_key
    }
    response = requests.get(url, headers=headers)

    return response.json()


def get_policy_object_group_detail(organizationId, policyObjectGroupId):
    url = base+f'/organizations/{organizationId}/policyObjects/groups/{policyObjectGroupId}'
    headers = {
        "Content-Type": "application/json",
        "X-Cisco-Meraki-API-KEY": api_key
    }
    response = requests.get(url, headers=headers)

    return response.json()


def create_policy_object_group(organizationId, parameters):
    url = base+f'/organizations/{organizationId}/policyObjects/groups'
    headers = {
        "Content-Type": "application/json",
        "X-Cisco-Meraki-API-KEY": api_key
    }
    response = requests.post(url, headers=headers, json=parameters)
    return response.json()


def update_policy_objects_group(organizationId, policyObjectGroupId, parameters):
    url = base+f'/organizations/{organizationId}/policyObjects/groups/{policyObjectGroupId}'
    headers = {
        "Content-Type": "application/json",
        "X-Cisco-Meraki-API-KEY": api_key
    }
    response = requests.put(url, headers=headers, json=parameters)
    return response.json()


def delete_policy_objects_group(organizationId, policyObjectGroupId):
    url = base+f'/organizations/{organizationId}/policyObjects/groups/{policyObjectGroupId}'
    headers = {
        "Content-Type": "application/json",
        "X-Cisco-Meraki-API-KEY": api_key
    }
    response = requests.delete(url, headers=headers)
    return response.text

## Policy Objects (individual) ##

def get_all_policy_objects(organizationId):
    url = base+f"/organizations/{organizationId}/policyObjects"
    headers = {
        "Content-Type": "application/json",
        "X-Cisco-Meraki-API-KEY": api_key
    }
    response = requests.get(url, headers=headers)
    return response.json()


def create_policy_object(organizationId, parameters):
    # Template for policy object at the top of the program
    url = base+f"/organizations/{organizationId}/policyObjects"
    headers = {
        "Content-Type": "application/json",
        "X-Cisco-Meraki-API-KEY": api_key
    }
    response = requests.post(url, headers=headers, params=parameters)
    return response.json()


def delete_policy_object(organizationId, policyObjectId):
    url = base+f"/organizations/{organizationId}/policyObjects/{policyObjectId}"
    headers = {
        "Content-Type": "application/json",
        "X-Cisco-Meraki-API-KEY": api_key
    }
    response = requests.delete(url, headers=headers)
    return response.text


def delete_matching_policy_objects(organizationId, identifier=""):
    """Deletes all policy objects with the identifier in the name (default is ALL)"""
    responses = []
    all_objects = get_all_policy_objects(organizationId)
    for policy_object in all_objects:
        if identifier.lower() in policy_object['name'].lower():
            response = delete_policy_object(organizationId, policy_object['id'])
            print('Removed ' + str(policy_object['name']))
            time.sleep(0.25)    # Rate limit for Meraki is 5 requests per second, limit to 4 per second to be sure
    return responses


def delete_everything(organizationId):
    """Deletes all policy objects AND policy object groups with the identifier in the name (default is ALL)"""
    responses = []
    all_objects = get_policy_objects_groups(organizationId)
    for policy_object_group in all_objects:
            response = delete_policy_objects_group(organizationId, policy_object_group['id'])
            responses.append(response)
            print(response)
            time.sleep(0.25)    # Rate limit for Meraki is 5 requests per second, limit to 4 per second to be sure

    responses.append(delete_matching_policy_objects(organizationId, identifier=""))

    return responses


def List_to_Policy_Group(organizationId, input_list, prefix, list_type='cidr', policy_group_name='Auto-Group'):
    '''Function accepts a LIST of either CIDRs or FQDNs and converts them to policy object entries then groups them under a
    single Policy Object Group in the Meraki Dashboard'''
    # if list_type != 'cidr' or list_type != 'fqdn':
    #     print("ERROR: Type should be one of 'cidr' OR 'fqdn'")
    #     return -1

    count = 0
    responses = []

    # Create policy objects for each cidr in the list
    objectsIds = []
    for entry in input_list:
        policy_object = {'name': f'{prefix}-{count}', 'type': f'{list_type}', 'category': 'network', f'{list_type}': f'{entry}'}
        object_request = create_policy_object(organizationId, policy_object)
        responses.append(object_request)
        objectsIds.append(int(object_request['id']))
        count = count + 1
        print(f'Created object {entry}')
        time.sleep(0.25) # Need to stay under 5 requests per second

    # Create a policy object group which includes all of the objects
    policy_group = {'name': f'{policy_group_name}', 'category': 'NetworkObjectGroup', 'objectIds': objectsIds}
    group_request = create_policy_object_group(org_id, policy_group)
    if "Name already exists" in json.dumps(group_request):  # If group exists, update it
        all_groups = get_policy_objects_groups(organizationId)
        for group in all_groups:
            if group['name'] == policy_group_name:
                update_request = update_policy_objects_group(organizationId, group['id'], policy_group)
                responses.append(update_request)
                print(update_request)
                return  responses

    return responses

