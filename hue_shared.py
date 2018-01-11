#!/usr/bin/python

import os, sys, string, json
import requests

tokens_fname = "config/PHILIPS_HUE.cfg"

bridge_ip = ""
token = ""

def token_status():
    load()
    return token != ""

def bridgeip():
    load()
    return bridge_ip

def load():
    global bridge_ip
    global token
    
    res = 0
    
    if os.path.isfile(tokens_fname):
        with open (tokens_fname, "r") as f:
            frl = f.readlines()
            frll = len(frl)
            bridge_ip = frl[0].replace("\n", "")
            if frll > 1:
                token = frl[1].replace("\n", "")
            res = 1
    else:
        res = 0
        
    return res

def get_sensors():
    burl = base_url()
    if burl != 0:
        url = '{0}/sensors'.format(burl)
        resp = requests.get(url)
        resp_json = resp.json()
        
        return_array = []
        
        for sensor in resp_json:
            _sen = resp_json[sensor]
            _sentype = _sen['type']
            if _sentype == "ZLLTemperature":
                rawtempstr = _sen["state"]["temperature"]
                floattemp = float(rawtempstr) / 100
                value = ("%0.2f" % floattemp)
                return_array.append( {"id":_sen["uniqueid"], "name":_sen["name"], "type": "temperature", "lastupdated": _sen["state"]["lastupdated"], "value": value} )
            elif _sentype == "ZLLPresence":
                value = "1"
                return_array.append( {"id":_sen["uniqueid"], "name":_sen["name"], "type": "presence", "lastupdated": _sen["state"]["lastupdated"], "value": value} )
    
        return return_array
    else:
        return 0

def base_url():
    load()
    if bridge_ip != "" and token != "":
        return 'http://{0}/api/{1}'.format(bridge_ip, token)
    else:
        return 0
    
def bridge_status():
    load()
    if bridge_ip != "" and token != "":
        url = '{0}/config'.format(base_url())
        resp = requests.get(url)
        resp_json = resp.json()
        return str(resp_json)

def request_token():
    load()
    if bridge_ip != "":
        url = 'http://{0}/api'.format(bridge_ip)
        post_fields = '{"devicetype":"homebot#smart_home_integration"}'
        resp = requests.post(url, data=post_fields)
        res_obj = resp.json()
        if len(res_obj) == 1:
            if 'success' in res_obj[0]:
                token = res_obj[0]['success']['username']
                set_token(token)

    return token_status()
    
def set_bridge_ip(bip_in):
    load()
    global bridge_ip
    bridge_ip = bip_in
    return write_token_file(bridge_ip, token)
    
def write_token_file(_bip, _tok):
    print("Setting Philips Hue cfg.. {0} - {1}".format(_bip, _tok))
    f = open(tokens_fname, "w")
    f.write(_bip)
    f.write("\n")
    f.write(_tok)
    f.close()
    return 1

def set_token(token_in):
    load()
    global token
    token = token_in
    return write_token_file(bridge_ip, token)
