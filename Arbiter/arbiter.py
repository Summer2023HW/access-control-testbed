import socket
import re

unknown = []
appliances = []
smart_meters = []
devices = []
id = "arbiter"
TCP_PORT = 5005

class Connection:
  id = ""
  type = ""
  ip = ""
  socket

  def __init__(self, in_ip):
    self.ip = in_ip

  def open(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((self.in_ip, TCP_PORT))
    self.socket.send("auth arbiter who")
    data = self.socket.recvfrom(1024).decode().split()

  def method(self):
    return id

def scan_network():
  unknown.append("192.168.2.11")

try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind(('', TCP_PORT))
  sock.listen(24)
  print("Successful binding of local socket")
except:
  print("Failure to bind local socket")

while True:
  scan_network()
  for x in unknown:
