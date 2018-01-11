#!/usr/bin/python

import homebot, slack_shared, hue_shared
import os, sys, hashlib, time, string
from flask import Flask, request, send_from_directory, redirect, url_for

# Flask
app = Flask(__name__)

@app.route("/slack_test", methods=["GET", "POST"])
def slack_test():
    slack_shared.message("User token test.", 0)
    slack_shared.message("Bot token test.", 1)
    html = web_header()
    html += 'You should have received two notificiations.<br/><a href="/">Back...</a>'
    html += web_footer()
    return html

@app.route("/", methods=["GET"])
def web_homepage():
    # header
    html = web_header()

    p_data = request.args
    if "arm" in p_data:
        t = p_data['arm']
        homebot.set_arm_state(t)
        return redirect(url_for('web_homepage'))

    state = homebot.arm_status()
    arm_disabled = "btn-primary"
    disarm_disabled = "btn-default disabled"
    friendly_state = "disarmed"
    if state:
        friendly_state = "armed"
        arm_disabled = "btn-default disabled"
        disarm_disabled = "btn-danger"

    # status panel
    html += '<div class="panel panel-default"><div class="panel-heading">Status</div><div class="panel-body">'
    html += '<div>HomeBot webserver is running. System is {0}.</div><br>'.format(friendly_state)
    html += '''<div class="btn-group" role="group" aria-label="...">
        <a type="button" class="btn btn-default {0}" href="/?arm=1">Arm</a>
        <a type="button" class="btn btn-default {1}" href="/?arm=0">Disarm</a>
    </div>'''.format(arm_disabled, disarm_disabled)
    html += '</div></div>'

    # slack panel
    html += '<div class="panel panel-default"><div class="panel-heading">Slack</div><div class="panel-body">'
    if slack_shared.check_auth_tokens():
        html += '<p>Configured&nbsp;&nbsp;<span class="glyphicon glyphicon-ok-circle" aria-hidden="true"></span><br><br><a class="btn btn-primary" role="button" href="/slack_test">Test</a></p>'
    else:
        html += '<p>Not configured&nbsp;&nbsp;<span class="glyphicon glyphicon-remove-sign" aria-hidden="true"></span><br><br><a class="btn btn-primary" role="button" href="/auth_slack">Setup</a></p>'
    html += '</div></div>'
    
    # philips hue panel
    html += '<div class="panel panel-default"><div class="panel-heading">Philips Hue</div><div class="panel-body">'
    if hue_shared.token_status():
        html += '<p>Configured&nbsp;&nbsp;<span class="glyphicon glyphicon-ok-circle" aria-hidden="true"></span><br><br><a class="btn btn-primary" role="button" href="/hue_test">Test</a></p>'
    else:
        html += '<p>Not configured&nbsp;&nbsp;<span class="glyphicon glyphicon-remove-sign" aria-hidden="true"></span><br><br><a class="btn btn-primary" role="button" href="/auth_hue">Setup</a></p>'
    html += '</div></div>'

    # footer
    html += web_footer()
    return html

@app.route("/auth_slack", methods=["GET", "POST"])
def slack_pre_install():
    just_loaded = 0
    p_data = request.form
    if "slack-client-id" in p_data and "slack-client-secret" in p_data and "slack-verf-token" in p_data and "slack-redirect-uri" in p_data:
        print("* slack_pre_install: Posted data available in request form")
        
        key_file = open(slack_shared.client_keys_fname, "w")
        key_file.write(p_data['slack-client-id'])
        key_file.write("\n")
        key_file.write(p_data['slack-client-secret'])
        key_file.write("\n")
        key_file.write(p_data['slack-verf-token'])
        key_file.write("\n")
        key_file.write(p_data['slack-redirect-uri'].lower())
        key_file.close()
        just_loaded = 1
    else:
        print("* slack_pre_install: Posted data NOT in request form")
    
    loaded = slack_shared.load_client_keys()
    
    html = web_header()
    if loaded:
        if just_loaded:
            html += "<p>Successfully saved client keys.</p>"
        html += '<p><a href="{0}" class="btn btn-info" role="button">Add to Slack</a></p>'.format( slack_shared.oauth_url() )
        #print('https://slack.com/oauth/authorize?scope={0}&client_id={1}&redirect_uri={2}'.format(slack_oauth_scopes, slack_client_id, slack_redirect_uri))
    else:
        html += '<p>Client keys not set, please <a target="_blank" href="https://api.slack.com/slack-apps">create a new app</a> and enter the details below.<br/>'
        html += 'Redirect URI should be entered in this format "http://homebot.domain:5000/auth_slack_finish" and all lower case when creating the app.</p>'
        html += '''
        <form action="/auth_slack" method="post">
            <div class="form-group">
              <label for="slack-client-id">Client ID:</label>
              <input type="text" class="form-control" name="slack-client-id">
            </div>
            <div class="form-group">
              <label for="slack-client-secret">Client Secret:</label>
              <input type="password" class="form-control" name="slack-client-secret">
            </div>
            <div class="form-group">
              <label for="slack-verf-token">Verification Token:</label>
              <input type="text" class="form-control" name="slack-verf-token">
            </div>
            <div class="form-group">
              <label for="slack-redirect-uri">Redirect URI:</label>
              <input type="text" class="form-control" placeholder="http://homebot.domain:5000/auth_slack_finish" name="slack-redirect-uri">
            </div>
            <button type="submit" class="btn btn-default">Submit</button>
        </form>
        '''
    html += web_footer()
    return html

@app.route("/auth_slack_finish", methods=["GET", "POST"])
def slack_post_install():
    # Retrieve the auth code from the request params
    slack_auth_code = request.args['code']
    auth_success = slack_shared.set_auth_tokens(slack_auth_code)
    
    html = web_header()
    if auth_success:
        html += 'Slack authentication set up correctly!<br/><br/><a class="btn btn-info" role="button" href="/">Back...</a>'
    else:
        html += 'Slack authentication failed, please <a href="/auth_slack">try again</a>.'
    html += web_footer()
    return html

@app.route("/auth_hue", methods=["GET", "POST"])
def auth_hue():
    just_loaded = 0
    p_data = request.form
    if "philips-hue-ip" in p_data:
        hue_shared.set_bridge_ip(p_data['philips-hue-ip'])
        just_loaded = 1
    elif "philips-hue-retry" in p_data:
        hue_shared.request_token()
    else:
        print("* slack_pre_install: Posted data NOT in request form")
    
    html = web_header()

    bip = hue_shared.bridgeip()
    tstatus = hue_shared.token_status()
    
    if bip == "":
        html += '<p>Please press the button on the Philips Hue bridge and then (within 30 seconds) submit the bridge IP below.</p>'
        html += '''
            <form action="/auth_hue" method="post">
                <div class="form-group">
                  <label for="philips-hue-ip">Bridge IP:</label>
                  <input type="text" class="form-control" name="philips-hue-ip">
                </div>
                <button type="submit" class="btn btn-default">Submit</button>
            </form>
            '''
    elif tstatus == 0:
        html += '<p>Philips Hue integration ({0}) not complete, please press the button on the bridge and then press retry.</p>'.format(bip)
        html += '''
            <form action="/auth_hue" method="post">
                <input type="hidden" value="retry" name="philips-hue-retry">
                <button type="submit" class="btn btn-default">Retry</button>
            </form>
            '''
    else:
        html += 'Configured correctly!<br/><br/><a class="btn btn-info" role="button" href="/">Back...</a>'
        
    html += web_footer()
    return html

@app.route("/hue_test", methods=["GET", "POST"])
def hue_test():    
    html = web_header()
    html += hue_shared.bridge_status()
    html += '<br/><br/><a class="btn btn-info" role="button" href="/">Back...</a>'
    html += web_footer()
    return html

static_files_directory = "website_static"

@app.route('/js/<path:path>')
def web_send_js(path):
    return send_from_directory('{0}/js'.format(static_files_directory), path)

@app.route('/css/<path:path>')
def web_send_css(path):
    return send_from_directory('{0}/css'.format(static_files_directory), path)

@app.route('/fonts/<path:path>')
def web_send_fonts(path):
    return send_from_directory('{0}/fonts'.format(static_files_directory), path)

def web_header():
    html = '''
    <!doctype html>

    <html lang="en">
    <head>
      <meta charset="utf-8">

      <title>HomeBot</title>
      <meta name="description" content="HomeBot">
      <meta name="author" content="Pr09het">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="stylesheet" href="css/bootstrap.min.css">

      <link rel="stylesheet" href="css/main.css?v=1.0">

      <!--[if lt IE 9]>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.3/html5shiv.js"></script>
      <![endif]-->
    </head>

    <body>
        <div class="container">
            <h1>HomeBot</h1>
            <div></div>
    '''
    return html

def web_footer():
    html = '''
        </div> <!-- .container -->
        <script src="js/main.js"></script>
        <script src="js/jquery.min.js"></script>
        <script src="js/bootstrap.min.js"></script>
    </body>
    </html>'''
    return html

if __name__ == "__main__":
    app.run(host= '0.0.0.0')
