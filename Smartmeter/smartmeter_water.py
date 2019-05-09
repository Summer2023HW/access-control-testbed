import socket
import time
import random
import subprocess
import re

UDP_IP = "0.0.0.0"
UDP_PORT = 5005
id = 'smart_meter'
type = 'electric'
int total_consumption = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
  data, addr = sock.recvfrom(1024)
  components = data.split()
  #verification
  if(components[0] == 'appliance'):
    val = re.search("w:\d+", str(components[1]))
    val = val.split("w:")[0]
    total_consumption += int(val)
  elif(components[0] == 'device'):
    #verify
    send_socket.sendto(str(total_consumption).encode(), (addr, UDP_PORT))
  elif(components[0] == 'arbiter'):
    #verify
    send_socket.sendto(id.encode(), (addr, UDP_PORT))
