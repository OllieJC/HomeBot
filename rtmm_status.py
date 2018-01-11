def enabled():
    return True

def initial_run(input_text):
    return False

def run(input_text):
    return "Not available yet."

def commands():
    if not enabled():
        return False

    return [
        {"command": "status", "text": "returns HomeBot status", "args": "0"}
    ]
