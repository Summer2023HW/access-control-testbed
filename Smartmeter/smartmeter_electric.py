import socket
import _thread
import re

electric = 0
TCP_PORT = 5005

id = 'smart_meter'
type = 'electric'

def make_receptive (ip_address):
  try:
    new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    new_sock.bind((ip_address, TCP_PORT))
    new_sock.listen(1)
    print("Successfully bound to socket at ip: " + ip_address)
  except:
    print("Failure to bind socket to ip: " + ip_address)
  while True:
    data = new_sock.recvfrom(1024).decode().split()
    print("Received Message from " + new_sock.getsockname() + ": " + str(data))
    if(authorize(data[0])):
      val = re.search("e:\d+", str(components[1]))
      val = val.split("e:")[0]
      electric += int(val)
    print("Total Electric Count: " + electric)

def respond_device (sock):
  sock.send(str(electric).encode())
  sock.shutdown(socket.SHUT_RDWR)
  sock.close()

def authorize(auth):
  return True

def authenticate():
  return "auth"

try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(('', TCP_PORT))
  sock.listen(12)
  print("Successful binding of local socket")
except:
  print("Failure to bind local socket")

while True:
  conn, address = sock.accept()
  conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  info, addr = conn.recvfrom(1024)
  info = info.decode().split()
  print("Received Message: " + str(info))
  if(authorize(info[0])):
    if(info[1] == "arbiter"):
      if(info[2] == "who"):
        conn.send((authenticate() + " " + id + " " + type).encode())
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
      elif(info[2] == "new_ip"):
        conn.send()
        _thread.start_new_thread(make_receptive(info[3],))
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
    elif(info[1] == "device"):
      respond_device(conn)
