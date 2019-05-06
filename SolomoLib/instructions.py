import sys, os
import imp
import csv
from flask import current_app as app
from importlib import import_module
from SolomoLib import SimpleRequest
#from custom import *


def query(query, appconfig, accounts, results):

	query_dir = appconfig['TOP_LEVEL_DIR'] + appconfig['QUERY_DIR'] + query['name']
	q = open(query_dir, 'r').read()
	#print(q.read())
	sf = accounts[query['account']]
	results = sf.query_all(q)
	return results

def endpoint(instruction, config, accounts):

	#print('username {} - password {} - url {} - {} - {}'.format(accounts[instruction['account']]['endpoint']['username'], accounts[instruction['account']]['endpoint']['password'], instruction['url'], instruction, accounts[instruction['account']]))

	req = SimpleRequest.Generic(accounts[instruction['account']]['endpoint']['username'], accounts[instruction['account']]['endpoint']['password'], instruction['url'], '')
	response = req.GetEndPoint(False)
	print(response)

def custom(instruction, appconfig, accounts, results):
	file = instruction['file']

	module = import_module("custom.{}".format(instruction['file']))
	
	results = getattr(module, instruction['method'])(results)
