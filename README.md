# HomeBot

HomeBot is a Python (2.7 / 3.6 compatible) home automation program designed to run on a small server/VM or embedded computer (Raspberry Pi!) and integrate with Slack

----

Their are 3 main scripts to run :-
- *homebot_webserver.py* - runs a Flask webserver on http://localhost:5000
- *philips_hue_sensors.py* - monitors Philips Hue motion sensors (requires bridge on same network)
- slack_rtm_listener.py - monitors Slack channel (currently hardcoded to _#home_, requires setting up a Slack app) 

`Major todo is to make this automated and either have a single script handler or service installer (or both)`
