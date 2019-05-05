import requests
import json


class Generic(object):
    
    def __init__(self, token_required, token, url, uri):
        self.username = username
        self.password = password
        self.token_required
        self.base_url = url
        self.states = {}
        self.countries = {}
        

    def GenericEndPoint(self, payload, debug):
        userid = 0
        headers = {
            'content-type': "application/json",
            'accept': "application/json",
        }

        complete_url = self.base_url + self.uri
        if self.token_required is True:
            r = requests.post(complete_url, data=payload, headers=headers, auth=(self.username, self.password) )
        elif self.token_required is False: 
            r = requests.post(complete_url, data=payload, headers=headers)
        if debug = True
            print('Results: {}'.format(r.text))
        return r.text
        
