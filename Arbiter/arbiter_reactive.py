import socket
import time
import random
import subprocess
import re

UDP_IP = "0.0.0.0"
UDP_PORT = 5005
id = 'arbiter'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
os.environ['send'] = ""

while True:
  data, addr = sock.recvfrom(1024)
  components = data.split()
  switch(data):
    case 'appliance':
      os.environ[addr] = data + " " + addr
    case 'smart_meter':
      os.environ[addr] = data + " " + addr
    case 'device':
      os.environ[addr] = data + " " + addr
