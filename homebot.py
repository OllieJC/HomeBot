#!/usr/bin/python
import os

# current working directory
cwd = os.getcwd()

# ARMED file: if exists, then system is armed
armed_fname = "config/ARMED.cfg"

def arm_status():
    return os.path.isfile(armed_fname)

def arm():
    open(armed_fname, 'w').close()
    return 1

def disarm():
    if status():
        os.remove(armed_fname)
    return 1

def set_arm_state(inputvar):
    if str(inputvar) == "0":
        disarm()
    else:
        arm()

modules_filenames = []
def set_modules_filenames():
    # set variable global, as we might set it
    global modules_filenames
    # if the 'modules_filenames' variable isn't set yet, then set
    if len(modules_filenames) == 0:
        for (dirpath, dirnames, filenames) in os.walk(cwd):
            for filename in filenames:
                # if a file starts with "rtmm_" and ends with ".py"
                # then add to 'modules_filenames' 
                if filename.startswith("rtmm_") and filename.endswith(".py"):
                    modules_filenames.append(filename)

modules_commands = []
def set_modules_commands():
    # module_filenames is required
    set_modules_filenames()
    
    # set variable global, as we might set it
    global modules_commands
    # if the 'modules_commands' variable isn't set yet, then set
    if len(modules_commands) == 0:
        for module_filename in modules_filenames:
            # remove ".py" from the filename
            module_name = module_filename[:-3]
            # attempt to import module and run 'commands' function
            try:
                module = __import__(module_name)
                # will return false if disabled - based on module 'enabled()' function
                res = module.commands()
            except:
                # fail gracefully
                print("Failed to load custom Real Time Messaging Module (rtmm) '{0}':".format(module_name), sys.exc_info()[0])
            finally:
                if res:
                    modules_commands.append({"module_name": module_name, "commands": res})
        modules_commands.append({"module_name": "special_help", "commands": [{"command":"help", "text":"(this)", "args": "0"}] })

def help_commands():
    res = ""
    help_items = []
    
    set_modules_commands()
    
    for module in modules_commands:
        for commands in module["commands"]:
            command = ""
            command_obj = commands["command"]
            if isinstance(command_obj, str):
                command = command_obj
            else:
                command = command_obj[0]
            command_text = commands["text"]
            help_items.append("- *{0}* - {1}\n".format(command, command_text))
            
    if len(help_items) != 0:
        help_items = sorted(help_items)
        res = ''.join(help_items)
    return res
        
# returns the module name based on the users input text
def return_module(input_text):
    # modules_commands is required
    set_modules_commands()
    
    print("Returning module for ", input_text)
    
    res = False
    
    for module in modules_commands:
        for commands in module["commands"]:
            if _is_module_match(commands["command"], input_text):
                res = module["module_name"]

    print("For the input '{0}' will run '{1}'...".format(input_text, res))

    return res

def _is_module_match(commands_obj, input_text):
    res = False
    
    if isinstance(commands_obj, str):
        #print("_is_module_match('{0}', '{1}')".format(commands_obj, input_text))
        if input_text.startswith(commands_obj):
            res = True
    else:
        for command in commands_obj:
            #print("_is_module_match('{0}', '{1}')".format(command, input_text))
            if input_text.startswith(command):
                res = True

    return res

def initial_run_module(input_text):
    module_name = return_module(input_text)
    if module_name:
        if module_name == "special_help":
            res = False
        else:
            module = __import__(module_name)
            res = module.initial_run(input_text)
        return res
    else:
        return False

def run_module(input_text):
    module_name = return_module(input_text)
    if module_name:
        if module_name == "special_help":
            res = help_commands()
        else:
            module = __import__(module_name)
            res = module.run(input_text)
        return res
    else:
        return False
