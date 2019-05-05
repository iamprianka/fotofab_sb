import os
from flask import request, current_app as app
from simple_salesforce import Salesforce

def load_configuration(fileName):
    fieldMap = {}
    fieldList = []
    fileName = app.config['FIELD_MAP_DIR']+fileName
    with open(fileName, "r") as config_data:
        for line in config_data:
            line = line.strip()
            if not line:  # line is blank
                continue
            if line.startswith("#"):  # comment line
                continue
            (key, val) = line.strip().split('=')
            fieldMap[key] = val
    return fieldMap

def salesforce_login():
    sf_object = Salesforce(
        username=app.config['SALESFORCE_USERNAME'],
        password=app.config['SALESFORCE_PASSWORD'],
        security_token=app.config['SALESFORCE_SECURITY_TOKEN'],
        sandbox=app.config['SALESFORCE_SANDBOX'])

    return sf_object

def solomo_login():
    sf_object = Salesforce(
        username=app.config['SOLOMO_SF_USERNAME'],
        password=app.config['SOLOMO_SF_PASSWORD'],
        security_token=app.config['SOLOMO_SF_SECURITY_TOKEN'],
        sandbox=app.config['SOLOMO_SF_SANDBOX'])

    return sf_object