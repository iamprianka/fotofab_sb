import requests
import json


class Generic(object):
    
    def __init__(self, username, password, url, uri):
        self.username = username
        self.password = password
        self.base_url = url
        self.uri = uri
        
    def get_username(self):
        return self.username

    def GetEndPoint(self, debug=False):
        userid = 0
        headers = {
            'content-type': "application/json",
            'accept': "application/json",
        }

        complete_url = self.base_url + self.uri
        print(complete_url)
        print('{} - {}'.format(self.username, self.password))
        exit(0)
        r = requests.get(self.base_url, auth=(self.username, self.password) )
        
        if debug is True:
            print('Results: {}'.format(r.text))
        return r.text

    def GenericEndPoint(self, payload, debug=False):
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
        if debug is True:
            print('Results: {}'.format(r.text))
        return r.text
        
