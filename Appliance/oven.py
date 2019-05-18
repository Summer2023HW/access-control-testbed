import socket
import time
import re
import random
import _thread

LIVE_CONNECTIONS = []
TCP_PORT = 5005

id = 'appliance'
type = 'oven'

def listen (socket):
  conn, address = socket.accept()
  info = conn.recv(1024).decode().split()
  print("Received Message: " + str(info))
  if(authorize(info[0])):
    if(info[1] == "arbiter"):
      if(info[2] == "who"):
        conn.send((authenticate() + " " + id + " " + type).encode())
        conn.close()
      elif(info[2] == "new_ip"):
        conn.send(b"Received, Disconnecting")
        conn.close()
        make_connection(info[3])
    conn.close()
  else:
    conn.send(b"Failed Authorization, Disconnecting")
    conn.close()

def authorize(info):
  return True

def authenticate():
  return "auth"

def make_connection(ip_address):
  new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    new_sock.connect((ip_address, TCP_PORT))
    print("Successful connection to ip: " + ip_address)
  except:
    print("Failure to connect to ip: " + ip_address)
  LIVE_CONNECTIONS.append(new_sock)

try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind(('', TCP_PORT))
  sock.listen(12)
  print("Successful binding of local socket")
except:
  print("Failure to bind local socket")

_thread.start_new_thread(listen, (sock,))

while True:
  numWat = random.randint(0, 0)
  numElec = random.randint(0, 200)
  message = "w:" + str(numWat) + " e:" + str(numElec)
  print("Sending message: '" + message + "' to ips:")
  for con in LIVE_CONNECTIONS:
    try:
      con.send(message.encode())
      print("  Live: " + str(con.getsockname()))
    except:
      LIVE_CONNECTIONS.remove(con)
      print("  Dead (Removed): " + str(con.getsockname()))
  time.sleep(5)
