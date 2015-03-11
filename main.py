import requests_unixsocket
import json
from time import sleep

def update_dns():
    session = requests_unixsocket.Session()
    r = session.get('http+unix://%2Fvar%2Frun%2Fdocker.sock/containers/json')
    if r.status_code != 200:
        return
    
