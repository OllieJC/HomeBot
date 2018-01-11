#!/usr/bin/python
import slack_shared, time, homebot

# load the authentication tokens
loaded = slack_shared.load_auth_tokens()

if not loaded:
    print("Slack not configured. Exiting in 5 seconds.")
    time.sleep(5)
    exit()

# create a slack client with the user token
sc = slack_shared.client(0)

# get the homebot id
homebot_id = ""
users_resp = sc.api_call("users.list")
if users_resp["ok"]:
    for member in users_resp["members"]:
        if member["name"] == "homebot":
            homebot_id = member["id"]

# get the #home channel id
home_channel_id = ""
channels_resp = sc.api_call("channels.list")
if channels_resp["ok"]:
    for channel in channels_resp["channels"]:
        if channel["name"] == "home":
            home_channel_id = channel["id"]

# use the user token to invite the chat bot
sc.api_call("channels.invite", channel=home_channel_id, user=homebot_id)

time.sleep(1)

# create a slack client with the bot token
sc = slack_shared.client(1)

def send_message(out_text):
    sc.api_call("chat.postMessage", channel=home_channel_id, text=out_text, username="HomeBot", icon_emoji=":house:")

if sc.rtm_connect(with_team_state=False):
    while True:
        events = sc.rtm_read()
        for event in events:
            if "text" in event and not "bot_id" in event:
                user_text = event["text"].lower().strip()
                
                module_initial_res = homebot.initial_run_module(user_text)
                if module_initial_res:
                    send_message(module_initial_res)
                    
                module_res = homebot.run_module(user_text)
                if module_res:
                    send_message(module_res)
            print(event)
        time.sleep(0.25)
else:
    print("Connection Failed")

