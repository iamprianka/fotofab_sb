##THIS APP IS USED TO PROCESS SCHEDULED JOBS##
import sys
import os, importlib
from flask import Flask, request, jsonify, current_app as app
from SolomoLib import Support as support, Util as util, Accounts, instructions
from json import dumps, loads, load
from collections import OrderedDict


def exec_job(config):
    # create the application object
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('kaupter.cfg')

    app_accounts = {}

    cur_dir = os.path.dirname(os.path.abspath(__file__))
    filename = "{0}/accounts/{1}".format(cur_dir, 'accounts.json')
    """with open(filename) as json_data:
        accounts = load(json_data)"""
        
    accounts = load(open(filename), object_pairs_hook=OrderedDict)

    service_accounts = []
    service_accounts = Accounts.load_accounts(accounts)

    results = {}
    for order in config['instructions'].keys():
        instruction = next(iter(config['instructions'][order]))
        print('@@@@ {}'.format(order))
        results = getattr(instructions, instruction)(config['instructions'][order][next(iter(config['instructions'][order]))], app.config, service_accounts, results)
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_names = sys.argv[1].split(',')

        cur_dir = os.path.dirname(os.path.abspath(__file__))

        for config_name in config_names:
            config_data = None

            filename = "{0}/config/{1}".format(cur_dir, config_name)
            config_data = load(open(filename), object_pairs_hook=OrderedDict)
            #with open(filename) as json_data:
                #print(load(json_data))
            #config_data = load(json_data)

            if config_data is not None:
                exec_job(config_data)
    else:
        print("specify the job as an arg")