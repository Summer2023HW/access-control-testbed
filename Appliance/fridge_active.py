import socket
import time
import random
import subprocess
import re
import os

UDP_IP = os.environ['ips'].split()
UDP_PORT = 5005
id = 'appliance'

count = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
  numWat = random.randint(0, 50)
  numElec = random.randint(0, 100)
  message = "w:" + str(numWat) + " e:" + str(numElec)
  print(message)
  for x in UDP_IP:
    print("send to: " + x)
    try:
      sock.sendto(message.encode(), (x, UDP_PORT))   #encode string; the Message.encode part is where we put the message
    except:
      UDP_IP.remove(x)
  time.sleep(5)
  count = (count + 1) % 3
  if(count == 0):
    UDP_IP = os.environ['ips'].split()
