from simple_salesforce import Salesforce

def dostuff():
    sf_object = Salesforce(
        username='dan@qbo.dev',
        password='salesforce1',
        security_token='bFnog0nT6653hMwx3lRzkKjnY',
        sandbox=False)

    accounts = sf_object.query("select Id from Account")
    for account in accounts['records']:
    	print(account)