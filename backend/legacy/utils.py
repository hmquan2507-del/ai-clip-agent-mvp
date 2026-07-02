import subprocess
import time

def run(cmd):
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

def now_ts():
    return int(time.time())
