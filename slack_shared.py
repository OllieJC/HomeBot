#!/usr/bin/python

import os, sys, string
from slackclient import SlackClient

# Slack :- variables
client_id = ""
client_secret = ""
verification_token = ""
client_keys_fname = "config/SLACK_CLIENT_KEYS.cfg"
tokens_fname = "config/SLACK_TOKENS.cfg"
token_user = ""
token_bot = ""
client_keys_set = 0
oauth_scopes = "bot,files:write:user,links:write,chat:write:bot,channels:history,channels:read,channels:write,users:read"
redirect_uri = ""

def oauth_url():
    load_client_keys()
    return "https://slack.com/oauth/authorize?scope={0}&client_id={1}&redirect_uri={2}".format(oauth_scopes, client_id, redirect_uri)

# Slack :- load client keys from the above 'client_keys_fname' file
def load_client_keys():
    global client_id
    global client_secret
    global verification_token
    global client_keys_set
    global redirect_uri
    
    if os.path.isfile(client_keys_fname):
        with open (client_keys_fname, "r") as client_keys_file:
            _tmp_keys = client_keys_file.readlines()
            client_id = _tmp_keys[0].replace("\n", "")
            client_secret = _tmp_keys[1].replace("\n", "")
            verification_token = _tmp_keys[2].replace("\n", "")
            redirect_uri = _tmp_keys[3].replace("\n", "").lower()
            client_keys_set = 1
    else:
        print("* load_client_keys: Slack client keys not set.")
        client_keys_set = 0
        
    return client_keys_set

def load_auth_tokens():
    global token_user
    global token_bot
    
    tokens_set = False
    
    if os.path.isfile(tokens_fname):
        with open (tokens_fname, "r") as tokens_file:
            _tmp_keys = tokens_file.readlines()
            token_user = _tmp_keys[0].replace("\n", "")
            token_bot = _tmp_keys[1].replace("\n", "")
            tokens_set = True
            
    return tokens_set

def client(bot):
    from slackclient import SlackClient
    loaded = load_auth_tokens()
    if loaded:
        token = ""
        if bot:
            token = token_bot
        else:
            token = token_user
        sc = SlackClient(token)
        return sc
    else:
        return False

def message(inputstr, bot):
    sc = client(bot)
    sc.api_call("chat.postMessage", channel="#home", text=inputstr, username="HomeBot", icon_emoji=":house:")

def check_auth_tokens():            
    return os.path.isfile(tokens_fname)

def set_auth_tokens(auth_code):
    auth_success = 0

    if auth_code != "":
        try:
            # An empty string is a valid token for this request
            sc = SlackClient("")
           
            # Request the auth tokens from Slack
            auth_response = sc.api_call(
                "oauth.access",
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                code=auth_code
            )
            print( auth_response )

            global token_user
            token_user = auth_response['access_token']
            
            global token_bot
            token_bot = auth_response['bot']['bot_access_token']
            
            if auth_response["ok"]:
                tokens_file = open(tokens_fname, "w")
                tokens_file.write(token_user)
                tokens_file.write("\n")
                tokens_file.write(token_bot)
                tokens_file.close()
                auth_success = 1
        except:
            print("Unexpected error:", sys.exc_info()[0])
            auth_success = 0

    return auth_success
