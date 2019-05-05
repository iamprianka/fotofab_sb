from flask import Blueprint, request, jsonify
from kaupter_app.transactions import transaction_api 
from kaupter_app.basic_auth import require_appkey
from flask import current_app as app
import json

transactions = Blueprint('transactions', __name__)

@transactions.route('/about', methods=['POST','GET'])
@require_appkey
def index():
    return "Solomo Platform v{}.  Created by Solomo 2018".format(app.config['VERSION'])

@transactions.route('/', methods=['POST','GET'])
@require_appkey
def home():
    return "Solomo API v{}".format(app.config['VERSION'])

@transactions.route('/fieldmapexample', methods=['POST','GET'])
@require_appkey
def fieldmap():
    return transaction_api.example_field_map('example_field_map.sdl')

@transactions.route('/account', methods=['POST'])
#@require_appkey
def process_account():
    print('@@@HERE@@@')
    #print('@@@@ACCOUNTS: {}'.format(request.get_json()))
    account_data = json.dumps(request.get_json(), ensure_ascii=False).encode('utf8')
    #------ANUDEEP MODIFIED-------FEB 22nd 2019----------
    transaction_api.processAccountInformation(request.get_json())
    #transaction_api.process_account(request.get_json())
    #----------------------------------------------------
    #print(request.get_json())
    return "OK", 200

@transactions.route('/contact', methods=['POST'])
#@require_appkey
def process_contact():
    #print('@@@@CONTACTS: {}'.format(request.get_json()))
    #transaction_api.process_contact(json.dumps(request.get_json(), ensure_ascii=False).encode('utf8'))
    #------------_ANUDEEP MODIFIED FEB 24 2019----------------------
    #transaction_api.process_contact(request.get_json())
    transaction_api.processContactInformation(request.get_json())
    #-----------------------------------------------------------------
    return "OK", 200


def format_response(payload):
    if payload == "[]": 
        return respond({ValueError("No match found"), 204}, None)
    else:
        return respond(None, payload)

def respond(err, res=None):
    response = {
        'statusCode': err["status"] if err else '200',
        'data': err["message"] if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }

    return jsonify(response)

