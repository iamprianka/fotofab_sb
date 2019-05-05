##THIS APP IS USED TO PROCESS SCHEDULED JOBS##
import sys
import os, importlib
from flask import Flask, render_template, request, abort, jsonify, current_app as app
from SolomoLib import Support as support, Util as util, accounts, instructions
from json import dumps, loads, load


def exec_job(config):
    # create the application object
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('kaupter.cfg')

    app_accounts = {}

    
    #Get the accounts required for the job
    if 'salesforce' in config['accounts']:
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        filename = "{0}/accounts/{1}".format(cur_dir, 'salesforce.json')
        with open(filename) as json_data:
            sf_accounts = load(json_data)
            
        if config['sandbox'] == 'True':
            sf_account = sf_accounts['salesforce_sandbox']
        else:
            sf_account = sf_accounts['salesforce']    
        sf_account['sandbox'] = config['sandbox']
        sf = accounts.salesforce(sf_account)
        app_accounts = dict([('salesforce', sf)])

    for instruction in config['instructions'].keys():

        results = getattr(instructions, instruction)(config['instructions'][instruction], app.config, app_accounts, results=None)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_names = sys.argv[1].split(',')

        cur_dir = os.path.dirname(os.path.abspath(__file__))

        for config_name in config_names:
            config_data = None

            filename = "{0}/config/{1}".format(cur_dir, config_name)
            print('@@@CUR DIR {}'.format(filename))
            with open(filename) as json_data:
                #print(load(json_data))
                config_data = load(json_data)

            if config_data is not None:
                exec_job(config_data)
    else:
        print("specify the job as an arg")