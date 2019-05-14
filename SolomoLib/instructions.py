import sys, os
import imp
import csv
from flask import current_app as app
from importlib import import_module
from SolomoLib import SimpleRequest, Util
from simple_salesforce import Salesforce
import json
from custom import rules
#from custom import *

times = 1
stuff = ''

def query(query, appconfig, accounts, results):

	query_dir = appconfig['TOP_LEVEL_DIR'] + appconfig['QUERY_DIR'] + query['name']
	q = open(query_dir, 'r').read()
	#print(q.read())
	sf = accounts[query['account']]
	results = sf.query_all(q)
	return results

def endpoint(instruction, config, accounts, data):

	thismodule = sys.modules[__name__]
	limit  = instruction['limit']
	offset = instruction['offset']

	username = accounts[instruction['account']]['username']
	password = accounts[instruction['account']]['password']

	req = SimpleRequest.Generic(username, password, instruction['url'], '')
	results = {}
	while True:

		response = req.GetEndPoint(limit, offset, False)

		#need to find a way to dynamically pass in the key
		if json.loads(response)['data'] > 0:
			results = json.loads(response)['data']
			offset = offset + limit
		else:
			break

		if len(json.loads(response)['data']) == 0:
			print('Job Complete')
			break
		
		for order in instruction['sub'].keys():
			sub = next(iter(instruction['sub'][order]))
			print(sub)
			results = getattr(thismodule, sub)(instruction['sub'][order][next(iter(instruction['sub'][order]))], config, accounts, results)

	return response

def iterate(instruction, config, accounts, data):

	response_list = []
	response_dict = {}
	map_data = Util.load_configuration(instruction['fieldmap'])
	
	for record in data:
		record_dict = {}
		for orig_field in map_data.keys():
			if orig_field in instruction['rules']:
				try:
					response_dict[map_data[orig_field]] = getattr(rules, instruction['rules'][orig_field])(record[orig_field])
				except Exception as e:
					response_dict = {}
					break

			elif "\:" in map_data[orig_field]:
				response_dict[map_data[orig_field].split("\:")[0]] = dict([(map_data[orig_field].split("\:")[1], record[orig_field])])
			else:
				response_dict[map_data[orig_field]] = record[orig_field]
		if len(response_dict) > 0:
			response_list.append(response_dict)
		response_dict = {}

	return response_list
	
def salesforce_action(instruction, appconfig, accounts, data):

	salesforce = accounts[instruction['account']]
	print('updating....')
    #retrieve the upsert key from the config file
	sObject = instruction['sobject']
	key = instruction['key']

	print('Batch Size {}'.format(len(data)))
	if len(data)>0:
		response = salesforce.bulk.__getattr__(sObject).upsert(data, key)    

		records_dict = []
		return response
	else:
		return None


def custom(instruction, appconfig, accounts, results=None):
	#file = instruction['file']
	print('here {}'.format(instruction))
	module = import_module("custom.{}".format(instruction['file']))
	
	results = getattr(module, instruction['method'])(instruction, appconfig, accounts, results)
	
def initialize(instruction, appconfig, accounts, results=None):
	#file = instruction['file']
	print('here {}'.format(instruction))
	module = import_module("custom.rules")
	print('@@@ Module Method: {}'.format(instruction['method']))
	results = getattr(module, instruction['method'])(instruction, appconfig, accounts, results)
	
def print_results(instruction, config, accounts, data):
	print(data)
	return data
