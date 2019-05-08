import socket
import time
import random
import subprocess
import re
import os

def update_ip_list():
    my_ip = subprocess.Popen(['hostname','-I'], stdout=subprocess.PIPE).communicate()[0]
    my_ip = str(my_ip).split()[0]
    os.environ['my_ip'] = my_ip
    my_ip = my_ip.split(".")
    p = subprocess.Popen(["ping ", my_ip[0] + "." + my_ip[1] + "." + my_ip[2] + ".255", "-b"], stdout=subprocess.PIPE, shell=True)
    p.kill()
    raw_ip = subprocess.Popen(['arp','-a'], stdout=subprocess.PIPE).communicate()
    expression = '\d+\.\d+\.\d+\.\d+'
    UDP_IP = re.findall(expression, str(raw_ip))
    return UDP_IP

UDP_IP = update_ip_list()
UDP_PORT = 5005
id = 'arbiter'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

os.environ['ip_list_full'] = str(UDP_IP)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
  appliances = []
  smart_meters = []
  devices = []
  for x in os.environ['ip_list_full'].split():  #ip status format: [type] [ip] [list of outgoing ips]
    status = os.environ[x].split()
    if(len(status) < 1):
      message = "arbiter who " + os.environ['my_ip']
      try:
        sock.sendto(message.encode(), (x, UDP_PORT))
      except:
        os.environ[x] = 'fail 0'
    else:
      switch(status[0]):
        case 'appliance':
          appliances.append(status[1])
        case 'smart_meter':
          smart_meters.append(status[1])
        case 'device':
          devices.append(status[1])
  
  time.sleep(5)
