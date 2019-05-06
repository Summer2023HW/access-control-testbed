import socket
import time
import random
import subprocess
import re
import os

raw_ip = subprocess.Popen(['arp','-a'], stdout=subprocess.PIPE).communicate()
expression = '\d+\.\d+\.\d+\.\d+'
UDP_IP = re.findall(expression, str(raw_ip))
print(UDP_IP)
UDP_PORT = 5005
id = 'arbiter'

os.environ['ip_list_full'] = str(UDP_IP)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
