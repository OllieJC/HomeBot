def enabled():
    return True

def initial_run(input_text):
    if input_text == "restart" or input_text == "reboot":
        return "Must be root."
    elif input_text == "sudo restart" or input_text == "sudo reboot":
        return "Restarting..."

def run(input_text):
    import subprocess, sys
    if input_text == "sudo restart" or input_text == "sudo reboot":
        if sys.platform == "win32":
            subprocess.call(["shutdown", "-r", "/t", "0"])
        else:
            subprocess.call(["sudo", "reboot"])

def commands():
    if not enabled():
        return False

    return [
        {"command": ["restart", "reboot", "sudo restart", "sudo reboot"], "text": "restarts HomeBot host server/comp$
    ]
