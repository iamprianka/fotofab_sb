from flask import request, current_app as app
from simple_salesforce import Salesforce
from SolomoLib import Util as util

def create_support_ticket(data):
	fieldmap = util.load_configuration('./support/supportfieldmap.sdl')
	sf = util.solomo_login()
	support_ticket = {}

	support_ticket['Account__c'] = app.config['SOLOMO_SF_CLIENT_ID']
	support_ticket['OwnerId']=app.config['SOLOMO_OWNER_ID']
	for field in fieldmap.keys():
		support_ticket[fieldmap[field]] = data[field]

	print('@@@@CASE {}'.format(support_ticket))
	support_ticket_insert = sf.Support_Ticket__c.create(support_ticket) 