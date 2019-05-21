import socket
import _thread
import re

electric = 0
TCP_PORT = 5005

id = 'smart_meter'
type = 'electric'

'''
Main function that is called after all functions are defined; binds listening socket and responds to received messages.
'''

def main():
  sock = make_socket()
  bind_socket(sock, '', 12)

  while True:
    conn, address = sock.accept()
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    info, addr = conn.recvfrom(1024)
    info = info.decode().split()
    if(len(info) < 1):
      continue
    print("Received Message: " + str(info) + " from " + str(addr))
    if(authorize(info[0])):
      if(info[1] == "who"):
        send(conn, authenticate() + " " + id + " " + type)
      elif(info[1] == "new_ip"):
        send(conn, "Received")
        for x in info[2:]:
          _thread.start_new_thread(listen, (x,))
      elif(info[1] == "request"):
        respond_status(conn)
    else:
      send(conn, "Failed Authorization, Disconnecting")
      close_socket(conn)

'''
Given an ip, sets up socket to be responsive and react to expected input from that source
'''

def listen (ip_address):
  new_sock = make_socket()
  if(not connect_socket(new_sock, ip_address)):
    return
  while True:
    data, addr = new_sock.recvfrom(1024)
    data = data.decode().split()
    print("Received Message: " + str(data) + " from " + str(addr))
    if(authorize(data[0])):
      val = re.search("e:\d+", str(components[1]))
      val = val.split("e:")[0]
      electric += int(val)
    print("Total Electric Count: " + electric)

'''
Upon request, inform the caller of the status of this Smart Meter
'''

def respond_status (sock):
  send(sock, "Electric Usage: " + str(electric))
  close_socket(sock)

#-------  Generic Below  ----------------------------------------------------------------------

'''
Establish a connection to a given ip_address and store the created socket object in LIVE_CONNECTIONS
'''

def make_connection(ip_address):
  for ip in ip_address:
    new_sock = make_socket()
    if(connect_socket(new_sock, ip) and sum([1 for x in LIVE_CONNECTIONS if x[0] == ip_address]) < 1):
      LIVE_CONNECTIONS.append((ip, new_sock,))
    else:
      close_socket(new_sock)

'''
Manage the creation of a socket; setting initial values
'''

def make_socket():
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  return sock

'''
Manage the closing of a socket; calling shutdown and then closing
'''

def close_socket(sock):
  try:
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
  except:
    print("Error in Socket Closing - Potentially non-fatal")

'''
Manage the binding of a socket to listen to a defined ip address ('' for universal) at a default port with
a specified number of live connections on that socket permitted.
'''

def bind_socket(sock, ip, num_connections):
  try:
    sock.bind((ip, TCP_PORT))
    sock.listen(num_connections)
    print("Successful binding of socket to: " + ip)
    return True
  except:
    print("Failure to bind local socket to: " + ip)
    return False

'''
Manage the connecting of a socket to a defined ip address and default port
'''

def connect_socket(sock, ip):
  try:
    sock.connect((ip, TCP_PORT))
    print("Successful connection to ip: " + ip)
    return True
  except:
    print("Failure to connect to ip: " + ip)
    return False

'''
Manage the sending of a message by a defined socket
'''

def send(sock, message):
  try:
    sock.send(message.encode())
    return True
  except:
    print("Failure to send message via socket at ip: " + str(re.findall("\d+\.\d+\.\d+\.\d+", str(sock))))
    return False

'''
Authorize authentification key received from a message
'''

def authorize(info):
  return info == "auth"

'''
Generate authentification key to send with messages
'''

def authenticate():
  return "auth"

#----------------------------------------------------------------------------------------------

main()
