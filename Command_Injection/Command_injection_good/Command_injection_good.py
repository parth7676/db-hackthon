import subprocess

def ping_host_secure(hostname):
    try:
        result = subprocess.run(["ping", "-c", "1", hostname], capture_output=True, shell=False)
        return result.returncode
    except Exception as e:
        print(f"Error pinging host: {e}")
        return None