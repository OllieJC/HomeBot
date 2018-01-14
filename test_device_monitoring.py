import sys, subprocess, time

def ping_target(target):
    pingout = False
    
    ping_var = ["ping"]
    if sys.platform == "win32":
        ping_var.extend(["-n", "1"])
    else:
        ping_var.extend(["-c", "1"])
    ping_var.append(target)

    try:
        pingout = subprocess.check_output(ping_var)
    except:
        print "Error."

    if pingout:
        if "unreachable" in pingout:
            pingout = False
        elif "Received = 1" in pingout and "bytes=" in pingout:
            pingout = True
        else:
            pingout = False
        
    return pingout

lastseen = 0

while 1==1:
    res = ping_target("192.168.0.6")
    if res:
        print("Online!")
        lastseen = time.time()
    elif (lastseen - time.time()) > 600:
        print("Offline, but seen within 3 minutes.")
    else:
        print("Offline")
    time.sleep(2)
