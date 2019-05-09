import socket
import time
import random
import subprocess
import re

UDP_IP = "0.0.0.0"
UDP_PORT = 5005
id = 'appliance'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
  data, addr = sock.recvfrom(1024)  #let's pretend the format is: [type], [request], [information list]
  ip_addr = re.search("\d+\.\d+\.\d+\.\d+", str(addr)).group(0)
  components = data.split()
  #some kind of verification of the arbiter
  if(components[0] == 'arbiter'):
      if(components[1] == 'new_ip'):
          ip_list = os.environ['ips'].split()
          for x in range(2, len(components)):
            if(x not in ip_list):
                ip_list.append(x)
          os.environ['ips'] = str(ip_list)
      elif(components[1] == 'remove_ip'):
          ip_list = os.environ['ips'].split()
          for x in range(2, len(components)):
            ip_list.remove(x)
          new_ips = ''
          for x in ip_list:
            new_ips += ' ' + x
          os.environ['ips'] = new_ips
      elif(components[1] == 'who'):
          try:
            send_sock.sendto(id.encode(), (str(ip_addr), UDP_PORT))
          except:
            print('Error in sending message to ' + str(ip_addr))
