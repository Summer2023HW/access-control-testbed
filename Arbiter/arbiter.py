import socket
import re
import subprocess

connections = []
live_ip = []
id = "arbiter"
TCP_PORT = 5005

class Connection:
  id = ""
  type = ""
  ip = ""
  socket = None

  def __init__(self, in_ip):
    self.ip = in_ip

  def open(self):
    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.connect((self.ip, TCP_PORT))
      self.socket.send("auth arbiter who")
      data, addr = self.socket.recvfrom(1024)
      data = data.decode().split()
      auth = data[0]
      target_id = data[1]
      target_type = data[2]
      if(authenticate(auth)):
        self.id = target_id
        self.type = target_type
        connections.append(self)
      print("Successful connection to ip: " + self.ip)
    except:
      print("Failure to connect to ip: " + self.ip)

def scan_network():
  #subprocess.Popen(['./ping_network.sh'], stdout=subprocess.PIPE).communicate()
  raw_ip = subprocess.Popen(['arp','-a'], stdout=subprocess.PIPE).communicate()
  expression = '\d+\.\d+\.\d+\.\d+'
  return re.findall(expression, str(raw_ip))

def new_connection(ip):
  conn = Connection(ip)
  conn.open()

def authenticate(auth):
  return True;

try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(('', TCP_PORT))
  sock.listen(24)
  print("Successful binding of local socket")
except:
  print("Failure to bind local socket")

while True:
  for x in scan_network():
    if(x not in live_ip):
      _thread.start_new_thread(new_connection, (x,))
  for x in connections:
    if(x.id == "appliance"):
      x.SOL_SOCKET
    elif(x.id == "smartmeter"):
      x.sock
    elif(x.id == ""):
