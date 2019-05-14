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

    def GetEndPoint(self, limit=10, offset=0, debug=False):
        userid = 0
        headers = {
            'accept': "application/json",
        }
        print('LIMIT {} - OFFSET {}'.format(limit, offset))
        complete_url =  "{}{}?limit={}&offset={}".format(self.base_url, self.uri,limit, offset)
        
        print(complete_url)

        r = requests.get(complete_url,verify=False)
        
        if debug is True:
            print('Results: {}'.format(r.text))
        """if len(json.loads(r.text)['data']) == 0:
            return None"""
        return r.text

    def GenericEndPoint(self, payload, debug=False):
        userid = 0
        headers = {
            'content-type': "application/json",
            'accept': "application/json",
        }

        complete_url = self.base_url + self.uri
        #if self.token_required is True:
        r = requests.post(complete_url, data=payload, headers=headers, auth=(self.username, self.password) )
        """elif self.token_required is False: 
            r = requests.post(complete_url, data=payload, headers=headers)"""
        if debug is True:
            print('Results: {}'.format(r.text))
        return r.text
        
