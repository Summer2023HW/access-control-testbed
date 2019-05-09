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

send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
  data, addr = sock.recvfrom(1024)
  components = data.split()
  if(data == 'appliance'):
      os.environ[addr] = data + " " + addr
  elif(data == 'smart_meter'):
      os.environ[addr] = data + " " + addr
  elif(data == 'device'):
      os.environ[addr] = data + " " + addr
