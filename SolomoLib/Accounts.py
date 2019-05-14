from simple_salesforce import Salesforce
import json

def load_accounts(client):

    accounts = []
    services_objects = dict()    
    for account in client:

        print('@@@@ {}'.format(client))
        # if 'odbc' in client:
        #     connectionstring = client['odbc']['connectionstring']
    
        #     odbc_object = connect(connectionstring)
        #     if odbc_object is None:
        #         print("ODBC: Not authenticated ")
        #         return False
        #     else:
        #         services_objects['odbc'] = odbc_object
        #         print("ODBC: Authenticated.") 
        #print('@@@@CLIENT ACCOUNT {}'.format(account))
        if next(iter(client[account])) == 'salesforce':
            print(client[account]['salesforce'])   
        
            force_user = client[account]['salesforce']['username']
            force_pwd = client[account]['salesforce']['password']
            force_token = client[account]['salesforce']['token']
            sandbox = client[account]['salesforce']['sandbox'] == "True"
    
            sf_object = Salesforce(
                username=force_user,
                password=force_pwd,
                security_token=force_token,
                sandbox=sandbox)
    
            if sf_object is None or sf_object.session_id is None:
                print('Salesforce: Not authenticated as {}'.format(force_user))
                return False
            else:
                services_objects[account] = sf_object
                print('Salesforce: Authenticated as {}'.format(force_user))
        if next(iter(client[account])) == 'endpoint':

            endpoint = {}
            #accounts[instruction['account']]['endpoint']['username']
            endpoint['username'] = client[account]['endpoint']['username']
            endpoint['password'] = client[account]['endpoint']['password']
            services_objects[account] = endpoint
            #username = client[account]['endpoint']['username']
            #password = client[account]['endpoint']['username']
            #print(services_objects[account])
    
        """if 'solomo' in client:
            solomo_user = client['solomo']["username"]
            solomo_pwd = client['solomo']["password"]
            solomo_token = client['solomo']["token"]
            sandbox = client['solomo']["sandbox"] == "True"
    
            sf_solomo = Salesforce(
                username=solomo_user,
                password=solomo_pwd,
                security_token=solomo_token,
                sandbox=sandbox)
    
            if sf_solomo is None or sf_solomo.session_id is None:
                print('Salesforce: Not authenticated as {}'.format(solomo_user))
                return False
            else:
                services_objects['solomo'] = sf_solomo
                print('Salesforce: Authenticated as {}'.format(solomo_user))
    
        if 'eTouches' in client:
            et_object = eTouches(accountid=client['eTouches']['accountid'], accountkey=client['eTouches']['accountkey'])
            token = et_object.get_token()
    
            if et_object is None or token is None:
                print("eTouches: Not authenticated as {}".format(client['eTouches']['accountid']))
                return False
            else:
                services_objects['eTouches'] = et_object
                print("eTouches: Authenticated as {}".format(client['eTouches']['accountid']))
    
        if 'cms' in client:
            services_objects['cms'] = CMS(username=client['cms']['username'], password=client['cms']['password'], url=client['cms']['url'])
    
        if 'qbo' in client:
            #access_token, refresh_token, realmId, name=None
            print('@@AUTH: {}'.format(Auth))
            services_objects['qbo'] = Auth.Auth(client['qbo']['tokenfile'], client)
    
        if 'dbs' in client:
    
            dbs_object = DBS()
            if dbs_object is None:
                print("DBS: No Connection")
                return False
            else:
                services_objects['dbs'] = dbs_object
                print("DBS: Connection")
    
        if 'csv' in client:
    
            csv_object = CSV()
            if csv_object is None:
                print("CSV: No Connection")
                return False
            else:
                services_objects['csv'] = csv_object
                print("CSV: Connection")"""

    return services_objects

def salesforce(config):
    force_user = config['username']
    force_pwd = config['password']
    force_token = config['token']
    sandbox = config['sandbox']
    
    if sandbox == 'False':
        print('PRODUCTION')
        sf_object = Salesforce(
            username=force_user,
            password=force_pwd,
            security_token=force_token)
    elif sandbox == 'True':
        print('SANDBOX {}'.format(sandbox))
        sf_object = Salesforce(
            username=force_user,
            password=force_pwd,
            security_token=force_token,
            sandbox=True)

    return sf_object