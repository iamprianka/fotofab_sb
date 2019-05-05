import requests
import json


class Generic(object):
    
    def __init__(self, token, property, url):
        self.token = token
        self.property = property
        self.base_url = url
        
    def get_leads(self, start_date, end_date):
        headers = {
            'content-type': "application/json",
            'accept': "application/json",
            'X-ApiToken':self.token
        }
        url = self.base_url + "/v1/{}/leads/?start_date={}&end_date={}".format(self.property, start_date, end_date)
        print('URL {}'.format(url))
        response = requests.get(url, headers=headers )
        r = response.text
        return r

