import sys, os
import imp
import csv
from flask import current_app as app
from importlib import import_module
from SolomoLib import SimpleRequest, Util
from simple_salesforce import Salesforce
import json

part_dict = {}
def initialize_parts(instruction, appconfig, accounts, data):
    print(instruction['account'])
    sf = accounts[instruction['account']]
    parts = sf.query_all("SELECT Id,Part_Number__c FROM Part__c")
    for part in parts['records']:
        part_dict[part['Part_Number__c']] = part['Id']
    
    return None
        
def verify_part(partnumber):
    if partnumber in part_dict:
        return part_dict[partnumber]
    else:
        print('part not found')
        raise ValueError('location not found')
        