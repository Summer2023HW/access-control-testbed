import socket
import time
import random
import subprocess
import re

raw_ip = subprocess.Popen(['arp','-a'], stdout=subprocess.PIPE).communicate()
expression = '\d+\.\d+\.\d+\.\d+'
UDP_IP = re.findall(expression, str(raw_ip))
print(UDP_IP)
UDP_PORT = 5005
id = 'appliance'

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
