def enabled():
    return True

def initial_run(input_text):
    return False

def run(input_text):
    if input_text == "restart" or input_text == "reboot":
        return "Must be root."
    elif input_text == "sudo restart" or input_text == "sudo reboot":
        return "Restarting..."

def commands():
    if not enabled():
        return False

    return [
        {"command": ["restart", "reboot", "sudo restart", "sudo reboot"], "text": "restarts HomeBot host server/computer", "args": "0"}
    ]
