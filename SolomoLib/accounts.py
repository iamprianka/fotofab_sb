from simple_salesforce import Salesforce

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