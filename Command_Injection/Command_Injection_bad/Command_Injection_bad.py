# VULNERABLE
import os
def ping_host_vulnerable(hostname):
    command = f"ping -c 1 {hostname}"
    result = os.system(command)
    return result