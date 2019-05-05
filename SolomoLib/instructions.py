import sys, os
import imp
import csv
from flask import current_app as app
from importlib import import_module
#from custom import *


def query(query, appconfig, accounts, results):

	query_dir = appconfig['TOP_LEVEL_DIR'] + appconfig['QUERY_DIR'] + query['name']
	q = open(query_dir, 'r').read()
	#print(q.read())
	sf = accounts[query['account']]
	results = sf.query_all(q)
	return results

def custom(instruction, appconfig, accounts, results):
	file = instruction['file']

	module = import_module("custom.{}".format(instruction['file']))
	
	results = getattr(module, instruction['method'])(results)
