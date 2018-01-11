def enabled():
    # check if nmap is installed
    return True

def initial_run(input_text):
    return "Starting nmap scan.\nResults may take a few minutes..."

def run(input_text):
    import subprocess, re
    
    try:
        nmap_regex = 'report for ([^\s]+)(\s\(([^\)]+))?[\s\S]+Address\:\s([^\s]+)(\s\((.*)\))?'

        os_scan = 0
        scanarg = ""
        for item in ["scan host", "scan ip", "scan subnet"]:
            if input_text.startswith(item):
                scanarg = input_text.replace(item, "").strip()
                scantype = '-A'
                os_scan = 1

        if scanarg == "":
            import socket   
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)
            textregex = re.search('(\d+\.\d+\.\d+\.)\d+', IPAddr, re.IGNORECASE)
            if textregex:
                scanarg = "{0}0/24".format( textregex.group(1) )
                scantype = '-sP'
        
        if scanarg != "":
            nmap_output = subprocess.check_output(['nmap', '-R', scantype, scanarg])
            nmap_results = nmap_output.decode('utf8').split("Nmap scan")
            
            outstring = "*Scan Result* _for '{0}'_".format(scanarg)
            outstring += "\n-----------------"
            
            if os_scan:
                outstring += nmap_output.decode('utf8')
            else:
                outstring += "\n"
                for result in nmap_results:
                    m = re.search(nmap_regex, result)
                    if m:
                        outstring += "*"+m.group(1)+"*"
                        if m.group(3) != None:
                            outstring += "\n> " + m.group(3)
                        if m.group(4) != None:
                            outstring += "\n> " + m.group(4)
                        if m.group(6) != None:
                            outstring += " `" + m.group(6) + "`\n"
        else:
            outstring = "Error parsing nmap scan"
            
    except:
        outstring = "Error returning nmap results"
    
    return outstring

def commands():
    if not enabled():
        return False

    res = [
        {"command":["scan network", "scan net", "network scan", "nmap scan", "net scan"], "text":"nmap scan against local network", "args": "0"},
        {"command":["scan host", "scan ip", "scan subnet"], "text":"nmap (with OS detection) scan against specific host/ip/cidr", "args": "host/ip/cidr"}
    ]
    return res
