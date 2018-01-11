def enabled():
    return False

def initial_run(input_text):
    return False

def run(input_text):
    return "Hello world"

def commands():
    if not enabled():
        return False

    return [
        {"command": ["hello world", "world hello"], "text":"Basic 'hello world' test", "args": "0"},
        {"command": "test", "text": "Basic 'hello world' test", "args": "0"}
    ]
